"""Candidate-only NQ2024 definition supersession supplement.

The pure candidate API does not read Parquet, import the trading-research
package, or modify the generic definition index.  A separate registered-worker
wrapper is included below; it lazily imports the existing bounded readers only
when a worker explicitly calls ``run_supersession_probe``.

The original explicit-M interpretation remains available. The separate daily
snapshot interpretation requires retained acquisition/source binding and the
provider's definition-specific snapshot contract. Snapshot A records remain
A records; they are never relabeled as modifications or backdated.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


DBN_INSTRUMENT_DEF_DOC = "https://docs.rs/dbn/latest/dbn/struct.InstrumentDefMsg.html"
SNAPSHOT_DOC = "https://databento.com/docs/schemas-and-data-formats/instrument-definitions"
QUANTPAD_DOC = "https://api.quantpad.ai/external/openapi.json"
SNAPSHOT_SEMANTICS = "databento_active_definition_daily_snapshot_v1"
SUPPLEMENT_VERSION = "jumbo-nq2024-definition-supersession-v1"
PHYSICAL_COORDINATE_VERSION = "jumbo-physical-coordinate-v1"
NONRETROACTIVE_VERSION = "jumbo-definition-supersession-nonretroactive-v1"
DEFAULT_LATENCY_NS = 250_000_000
INT64_MAX = (1 << 63) - 1
MAX_DEFINITION_AUDIT_BYTES = 16 * 1024 * 1024
TARGET_ROOT = "NQ"
TARGET_YEAR = 2024
TARGET_YEAR_END_NS = 1_735_689_600_000_000_000
TARGET_INSTRUMENT_ID = 106364
TARGET_SYMBOL = "NQZ4"
TARGET_PUBLISHER_ID = 1
TARGET_INSTRUMENT_CLASS = "F"
TARGET_SECURITY_TYPE = "FUT"
UPDATE_ACTIONS = frozenset(("A", "M", "D"))
# Keep this gate aligned with data.ohlc._DEFINITION_FIELDS.  The registered
# reader's raw export does not carry publisher_id; the supplement treats that
# numeric field as optional evidence and never fabricates it when absent.
REGISTERED_DEFINITION_FIELDS = frozenset({
    "t", "ts_recv", "raw_symbol", "instrument_id", "instrument_class",
    "security_update_action", "activation", "expiration",
    "min_price_increment", "contract_multiplier",
})
RAW_AUDIT_REQUIRED_FIELDS = REGISTERED_DEFINITION_FIELDS
OPTIONAL_RAW_AUDIT_FIELDS = frozenset({"publisher_id"})
SOURCE_SUPERSESSION_STATUS = "source_supersession_supported_pending_price_readmission"


class SupersessionInputError(ValueError):
    """Malformed candidate supplement input."""


def _exact_int(value: Any, name: str, *, positive: bool = False) -> int:
    if (type(value) is not int or value > INT64_MAX or
            (value <= 0 if positive else value < 0)):
        relation = "positive" if positive else "nonnegative"
        raise SupersessionInputError(f"{name} must be an exact {relation} integer")
    return value


def _canonical_tick(value: Any) -> str:
    """Canonicalize a finite decimal tick without using binary arithmetic."""
    if isinstance(value, bool) or value is None:
        raise SupersessionInputError("tick size is required for the physical identity")
    text = str(value).strip()
    if not text:
        raise SupersessionInputError("tick size is required for the physical identity")
    try:
        # Decimal is deliberately imported locally so the source file stays a
        # pure standard-library candidate and never touches the data reader.
        from decimal import Decimal

        tick = Decimal(text)
    except Exception as exc:
        raise SupersessionInputError("tick size must be an exact decimal") from exc
    if not tick.is_finite() or tick <= 0:
        raise SupersessionInputError("tick size must be finite and positive")
    return format(tick.normalize(), "f")


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise SupersessionInputError("supplement identity fields must be JSON serializable") from exc


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _row_digest(row: Mapping[str, Any]) -> str:
    return _digest({str(key): value for key, value in row.items()})


def _text_enum(value: Any, name: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        try:
            value = value.rstrip(b"\x00").decode("ascii")
        except UnicodeDecodeError as exc:
            raise SupersessionInputError(f"{name} must be ASCII text") from exc
    if not isinstance(value, str):
        raise SupersessionInputError(f"{name} must be text")
    return value.rstrip("\x00").strip()


def _publisher(row: Mapping[str, Any], bound: str, *, expected_id: int) -> tuple[str, int | None]:
    value = row.get("publisher")
    if value is not None and value != bound:
        raise SupersessionInputError("raw definition publisher differs from the bound source publisher")
    actual_id = row.get("publisher_id")
    if "publisher_id" in row and actual_id is not None \
            and (type(actual_id) is not int or actual_id != expected_id):
        raise SupersessionInputError("raw definition publisher_id differs from the bound source publisher")
    return bound, actual_id if type(actual_id) is int else None


def _root(row: Mapping[str, Any], bound: str) -> str:
    value = row.get("root")
    if value is not None and value != bound:
        raise SupersessionInputError("raw definition root differs from the bound target root")
    return bound


def _validate_instrument_metadata(row: Mapping[str, Any], *, require_class: bool = False) -> tuple[str, str | None]:
    instrument_class = _text_enum(row.get("instrument_class"), "instrument_class")
    if require_class and instrument_class != TARGET_INSTRUMENT_CLASS:
        raise SupersessionInputError("raw definition instrument_class is not futures")
    if instrument_class is not None and instrument_class != TARGET_INSTRUMENT_CLASS:
        raise SupersessionInputError("raw definition instrument_class is not futures")
    security_type = _text_enum(row.get("security_type"), "security_type")
    if security_type is not None and security_type != TARGET_SECURITY_TYPE:
        raise SupersessionInputError("raw definition security_type is not futures")
    return instrument_class or TARGET_INSTRUMENT_CLASS, security_type


def _contract_key(root: str, instrument_id: int, raw_symbol: str,
                  activation_ns: int, expiration_ns: int) -> str:
    return f"{root}:{raw_symbol}:{instrument_id}:{activation_ns}:{expiration_ns}"


def _tick_value(row: Mapping[str, Any]) -> Any:
    if "min_price_increment" in row:
        return row.get("min_price_increment")
    return row.get("tick_size")


@dataclass(frozen=True)
class PhysicalCoordinate:
    """Raw physical coordinate with activation deliberately excluded.

    ``publisher_id`` is optional because this DBN-to-Parquet export omits the
    numeric publisher field; when absent, ``publisher`` and the retained
    source namespace provide the binding and the numeric value stays unknown.
    """

    root: str
    publisher: str
    instrument_id: int
    raw_symbol: str
    expiration_ns: int
    tick_size: str
    publisher_id: int | None = None

    @property
    def identity(self) -> str:
        payload = {
            "version": PHYSICAL_COORDINATE_VERSION,
            "root": self.root,
            "publisher": self.publisher,
            "publisher_id": self.publisher_id,
            "instrument_id": self.instrument_id,
            "raw_symbol": self.raw_symbol,
            "expiration_ns": self.expiration_ns,
            "tick_size": self.tick_size,
        }
        return f"{PHYSICAL_COORDINATE_VERSION}:{_digest(payload)}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": PHYSICAL_COORDINATE_VERSION,
            "identity": self.identity,
            "root": self.root,
            "publisher": self.publisher,
            "publisher_id": self.publisher_id,
            "instrument_id": self.instrument_id,
            "raw_symbol": self.raw_symbol,
            "expiration_ns": self.expiration_ns,
            "tick_size": self.tick_size,
        }


@dataclass(frozen=True)
class DefinitionUpdate:
    """Validated raw update metadata supplied by the registered worker."""

    source_index: int
    action: str
    coordinate: PhysicalCoordinate
    activation_ns: int
    event_at_ns: int
    provider_at_ns: int
    known_at_ns: int
    source_path: str
    source_row: int | None
    source_sha256: str | None
    raw_fields_sha256: str
    definition_version: str | None
    raw: Mapping[str, Any]
    contract_key: str | None = None
    instrument_class: str = TARGET_INSTRUMENT_CLASS
    security_type: str | None = TARGET_SECURITY_TYPE

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_index": self.source_index,
            "action": self.action,
            "coordinate": self.coordinate.as_dict(),
            "activation_ns": self.activation_ns,
            "event_at_ns": self.event_at_ns,
            "provider_at_ns": self.provider_at_ns,
            "chosen_receipt_ns": max(self.event_at_ns, self.provider_at_ns),
            "receipt_selection": "max(t,ts_recv)",
            "known_at_ns": self.known_at_ns,
            "known_at_policy": "max(t,ts_recv)+250ms",
            "source_path": self.source_path,
            "source_row": self.source_row,
            "source_sha256": self.source_sha256,
            "raw_fields_sha256": self.raw_fields_sha256,
            "definition_version": self.definition_version,
            "contract_key": self.contract_key,
            "publisher_id": self.coordinate.publisher_id,
            "instrument_class": self.instrument_class,
            "security_type": self.security_type,
        }


def _definition_update(
    row: Mapping[str, Any],
    source_index: int,
    *,
    root: str,
    publisher: str,
    latency_ns: int,
    expected_publisher_id: int = TARGET_PUBLISHER_ID,
    require_instrument_class: bool = False,
) -> DefinitionUpdate:
    if not isinstance(row, Mapping):
        raise SupersessionInputError("definition rows must be mappings")
    action = _text_enum(row.get("security_update_action"), "security_update_action")
    if action not in UPDATE_ACTIONS:
        raise SupersessionInputError("security_update_action is unknown or unsupported")
    instrument_id = _exact_int(row.get("instrument_id"), "instrument_id", positive=True)
    raw_symbol = row.get("raw_symbol")
    if not isinstance(raw_symbol, str) or not raw_symbol:
        raise SupersessionInputError("raw_symbol must be nonempty text")
    expiration_ns = _exact_int(row.get("expiration"), "expiration", positive=True)
    activation_ns = _exact_int(row.get("activation"), "activation")
    tick_size = _canonical_tick(_tick_value(row))
    if not isinstance(publisher, str) or not publisher:
        raise SupersessionInputError("bound publisher must be nonempty text")
    _root(row, root)
    publisher, publisher_id = _publisher(row, publisher, expected_id=expected_publisher_id)
    instrument_class, security_type = _validate_instrument_metadata(
        row, require_class=require_instrument_class
    )
    event_at_ns = _exact_int(row.get("t"), "definition event timestamp", positive=True)
    provider_at_ns = _exact_int(row.get("ts_recv"), "definition provider timestamp", positive=True)
    if type(latency_ns) is not int or latency_ns < 0:
        raise SupersessionInputError("latency_ns must be a nonnegative exact integer")
    known_at_ns = max(event_at_ns, provider_at_ns) + latency_ns
    _exact_int(known_at_ns, "definition known-at timestamp")
    source_path = row.get("source_path", "<raw-definition>")
    if not isinstance(source_path, str) or not source_path:
        raise SupersessionInputError("source_path must be nonempty text")
    source_row = row.get("source_row")
    if source_row is not None:
        source_row = _exact_int(source_row, "source_row")
    source_sha256 = row.get("source_sha256")
    if source_sha256 is not None and (not isinstance(source_sha256, str) or not source_sha256):
        raise SupersessionInputError("source_sha256 must be nonempty text when supplied")
    raw_fields_sha256 = row.get("raw_fields_sha256")
    if not isinstance(raw_fields_sha256, str) or not raw_fields_sha256:
        raw_fields_sha256 = _row_digest(row)
    definition_version = row.get("definition_version")
    if definition_version is not None and (not isinstance(definition_version, str) or not definition_version):
        raise SupersessionInputError("definition_version must be nonempty text when supplied")
    contract_key = row.get("contract_key")
    if contract_key is not None and (not isinstance(contract_key, str) or not contract_key):
        raise SupersessionInputError("contract_key must be nonempty text when supplied")
    if contract_key is None:
        contract_key = _contract_key(root, instrument_id, raw_symbol, activation_ns, expiration_ns)
    return DefinitionUpdate(
        source_index=source_index,
        action=action,
        coordinate=PhysicalCoordinate(root, publisher, instrument_id, raw_symbol,
                                      expiration_ns, tick_size, publisher_id),
        activation_ns=activation_ns,
        event_at_ns=event_at_ns,
        provider_at_ns=provider_at_ns,
        known_at_ns=known_at_ns,
        source_path=source_path,
        source_row=source_row,
        source_sha256=source_sha256,
        raw_fields_sha256=raw_fields_sha256,
        definition_version=definition_version,
        raw=dict(row),
        contract_key=contract_key,
        instrument_class=instrument_class,
        security_type=security_type,
    )


def _observed_start(row: Mapping[str, Any]) -> int:
    for name in ("start_ns", "t"):
        if name in row:
            return _exact_int(row[name], f"observed {name}")
    raise SupersessionInputError("observed row requires start_ns or t")


def _observed_end(row: Mapping[str, Any], start_ns: int) -> int:
    if "end_ns" not in row or row.get("end_ns") is None:
        return start_ns
    end_ns = _exact_int(row["end_ns"], "observed end_ns")
    if end_ns < start_ns:
        raise SupersessionInputError("observed end_ns must be at or after start_ns")
    return end_ns


def _observed_year(row: Mapping[str, Any], start_ns: int) -> int:
    raw_date = row.get("date")
    if raw_date is not None:
        if not isinstance(raw_date, str):
            raise SupersessionInputError("observed date must be an ISO string")
        try:
            parsed = date.fromisoformat(raw_date)
        except ValueError as exc:
            raise SupersessionInputError("observed date must be canonical ISO") from exc
        if parsed.isoformat() != raw_date:
            raise SupersessionInputError("observed date must be canonical ISO")
        return parsed.year
    try:
        return datetime.fromtimestamp(start_ns / 1_000_000_000, tz=timezone.utc).year
    except (OverflowError, OSError, ValueError) as exc:
        raise SupersessionInputError("observed timestamp cannot be mapped to a UTC year") from exc


def _unresolved(
    *,
    root: str,
    publisher: str,
    observed_count: int,
    reason_codes: Sequence[str],
    target_instrument_id: int,
    target_year: int,
    raw_actions: Sequence[Any],
) -> dict[str, Any]:
    return {
        "schema": SUPPLEMENT_VERSION,
        "status": "unresolved",
        "original_status": "unresolved",
        "actual_status": "unresolved",
        "actual_accepted": False,
        "root": root,
        "publisher": publisher,
        "publisher_id": None,
        "publisher_id_expected": TARGET_PUBLISHER_ID,
        "publisher_id_resolution": "unresolved",
        "target_year": target_year,
        "target_instrument_id": target_instrument_id,
        "observed_count": observed_count,
        "candidate_count": 0,
        "corrected_count": 0,
        "pre_known_count": observed_count,
        "reason_codes": tuple(dict.fromkeys(reason_codes)),
        "raw_actions": tuple(raw_actions),
        "price_readmission_pending": False,
        "generic_admission_untouched": True,
        "actual_validation_stage": "registered_check7_extract8",
        "dbn_instrument_definition_docs": DBN_INSTRUMENT_DEF_DOC,
    }


def _unresolved_result(report: Mapping[str, Any], observed: Sequence[tuple[Any, Mapping[str, Any], int, int]]) -> dict[str, Any]:
    pre_known = tuple(dict(row) for _, row, _, _ in observed)
    return {
        "report": dict(report),
        "candidate_canonical2024": (),
        "corrected_canonical2024": (),
        "pre_known_rows": pre_known,
        "expiry_excluded_rows": (),
    }


def _latest_known_compatible_update(
    updates: Sequence[DefinitionUpdate],
    coordinate: PhysicalCoordinate,
    start_ns: int,
) -> DefinitionUpdate | None:
    candidates = [
        update for update in updates
        if update.action in {"A", "M"}
        and update.coordinate == coordinate
        and update.known_at_ns <= start_ns
    ]
    if not candidates:
        return None
    newest_known = max(update.known_at_ns for update in candidates)
    latest = [update for update in candidates if update.known_at_ns == newest_known]
    if len(latest) != 1:
        raise SupersessionInputError("same-known-time compatible definitions are ambiguous")
    return latest[0]


def _retained_definition_version(update: DefinitionUpdate) -> tuple[str, str]:
    if update.definition_version:
        return update.definition_version, "retained_latest_known"
    return f"{NONRETROACTIVE_VERSION}:raw-fields:{update.raw_fields_sha256}", "candidate_raw_fields_fallback"


def build_definition_supersession_supplement(
    definition_rows: Sequence[Mapping[str, Any]],
    observed_rows: Sequence[Mapping[str, Any]],
    *,
    root: str = TARGET_ROOT,
    target_year: int = TARGET_YEAR,
    publisher: str = "quantpad",
    target_instrument_id: int = TARGET_INSTRUMENT_ID,
    target_symbol: str = TARGET_SYMBOL,
    latency_ns: int = DEFAULT_LATENCY_NS,
    publisher_id: int = TARGET_PUBLISHER_ID,
    snapshot_binding: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a source candidate without claiming price-table readmission.

    With the original interpretation a correction requires an actual
    changed ``M`` for one physical coordinate, an earlier ``A`` for that same
    publisher/ID/symbol/expiry/tick coordinate.  The numeric publisher_id is
    retained when the raw export supplies it; when the export omits that
    optional field, the exact bound publisher namespace and retained source
    path/hash remain the identity binding.  There is no deletion/unknown action or
    same-known-time conflict for the target ID, and activation/expiry terms
    that cover the observed bars.  The first changed M authorizes the source
    correction.  Each candidate bar then selects the latest compatible A/M
    already known at that bar; no future M is allowed to rewrite an earlier
    bar.  The pure API returns ``candidate_canonical2024`` only.  A registered
    The separately bound daily-snapshot interpretation instead accepts an
    active definition state from its own receipt plus the declared latency.
    Its A action is retained and no future snapshot authorizes earlier rows.
    A worker must reread the raw OHLC partition and perform the narrow
    ambiguous-only readmission before producing a corrected table.
    """
    if root != TARGET_ROOT or type(target_year) is not int or target_year != TARGET_YEAR:
        raise SupersessionInputError("this supplement is frozen to NQ2024")
    if type(target_instrument_id) is not int or target_instrument_id != TARGET_INSTRUMENT_ID:
        raise SupersessionInputError("this supplement is frozen to raw instrument 106364")
    if not isinstance(target_symbol, str) or target_symbol != TARGET_SYMBOL:
        raise SupersessionInputError("this supplement is frozen to NQZ4")
    if type(publisher_id) is not int or publisher_id != TARGET_PUBLISHER_ID:
        raise SupersessionInputError("this supplement is frozen to numeric publisher_id 1")
    if not isinstance(definition_rows, Sequence) or isinstance(definition_rows, (str, bytes)):
        raise SupersessionInputError("definition_rows must be an explicit sequence")
    if not isinstance(observed_rows, Sequence) or isinstance(observed_rows, (str, bytes)):
        raise SupersessionInputError("observed_rows must be an explicit sequence")

    observed = []
    observed_reasons: list[str] = []
    for index, row in enumerate(observed_rows):
        if not isinstance(row, Mapping):
            observed_reasons.append("malformed_observed_row")
            continue
        try:
            start_ns = _observed_start(row)
            end_ns = _observed_end(row, start_ns)
            if _observed_year(row, start_ns) != target_year:
                observed_reasons.append("observed_year_mismatch")
            if row.get("instrument_id") is not None and row.get("instrument_id") != target_instrument_id:
                observed_reasons.append("observed_instrument_mismatch")
            observed.append((index, row, start_ns, end_ns))
        except SupersessionInputError:
            observed_reasons.append("malformed_observed_row")
    if not observed:
        report = _unresolved(root=root, publisher=publisher, observed_count=0,
                             reason_codes=("no_observed_target_rows",),
                             target_instrument_id=target_instrument_id,
                             target_year=target_year, raw_actions=())
        return _unresolved_result(report, observed)
    if observed_reasons:
        report = _unresolved(root=root, publisher=publisher, observed_count=len(observed),
                             reason_codes=tuple(observed_reasons), target_instrument_id=target_instrument_id,
                             target_year=target_year, raw_actions=())
        return _unresolved_result(report, observed)

    target_raw = []
    malformed_target_rows = []
    for index, row in enumerate(definition_rows):
        if not isinstance(row, Mapping):
            malformed_target_rows.append("malformed_definition_row")
            continue
        if (row.get("instrument_id") == target_instrument_id
                or row.get("raw_symbol") == target_symbol):
            target_raw.append((index, row))
    updates: list[DefinitionUpdate] = []
    raw_actions: list[Any] = []
    reasons: list[str] = list(malformed_target_rows)
    for index, row in target_raw:
        action = None
        action_recorded = False
        try:
            action = _text_enum(row.get("security_update_action"), "security_update_action")
            raw_actions.append(action)
            action_recorded = True
            update = _definition_update(
                row, index, root=root, publisher=publisher, latency_ns=latency_ns,
                expected_publisher_id=publisher_id,
                require_instrument_class=snapshot_binding is not None,
            )
            if (update.coordinate.raw_symbol != target_symbol
                    or update.coordinate.instrument_id != target_instrument_id):
                reasons.append("target_coordinate_mismatch")
            else:
                updates.append(update)
        except SupersessionInputError:
            if not action_recorded:
                action = row.get("security_update_action")
                try:
                    action = _text_enum(action, "security_update_action")
                except SupersessionInputError:
                    action = None
                raw_actions.append(action)
            if action not in UPDATE_ACTIONS:
                reasons.append("unknown_security_update_action")
            else:
                reasons.append("malformed_target_definition_row")

    if not target_raw:
        reasons.append("no_target_definition_rows")
    if any(action not in UPDATE_ACTIONS for action in raw_actions):
        reasons.append("unknown_security_update_action")
    scoped_updates = [update for update in updates if update.known_at_ns <= TARGET_YEAR_END_NS]
    future_updates = [update for update in updates if update.known_at_ns > TARGET_YEAR_END_NS]
    scoped_actions = {update.action for update in scoped_updates}
    if "D" in scoped_actions:
        reasons.append("delete_action_preserved_unresolved")
    if len(updates) != len(target_raw) or reasons:
        report = _unresolved(root=root, publisher=publisher, observed_count=len(observed),
                             reason_codes=tuple(reasons), target_instrument_id=target_instrument_id,
                             target_year=target_year, raw_actions=raw_actions)
        return _unresolved_result(report, observed)

    coordinates = {update.coordinate for update in scoped_updates}
    if len(coordinates) != 1:
        report = _unresolved(root=root, publisher=publisher, observed_count=len(observed),
                             reason_codes=("physical_coordinate_conflict",),
                             target_instrument_id=target_instrument_id, target_year=target_year,
                             raw_actions=raw_actions)
        return _unresolved_result(report, observed)
    source_namespaces = {
        (update.source_path, update.source_sha256) for update in scoped_updates
    }
    if len(source_namespaces) != 1:
        report = _unresolved(root=root, publisher=publisher, observed_count=len(observed),
                             reason_codes=("source_namespace_conflict",),
                             target_instrument_id=target_instrument_id, target_year=target_year,
                             raw_actions=raw_actions)
        return _unresolved_result(report, observed)
    known_groups: dict[int, list[DefinitionUpdate]] = {}
    for update in scoped_updates:
        known_groups.setdefault(update.known_at_ns, []).append(update)
    if any(len(group) > 1 for group in known_groups.values()):
        report = _unresolved(root=root, publisher=publisher, observed_count=len(observed),
                             reason_codes=("same_known_at_conflict",), target_instrument_id=target_instrument_id,
                             target_year=target_year, raw_actions=raw_actions)
        return _unresolved_result(report, observed)

    additions = sorted((u for u in scoped_updates if u.action == "A"),
                       key=lambda u: (u.known_at_ns, u.source_index))
    modifications = sorted((u for u in scoped_updates if u.action == "M"),
                           key=lambda u: (u.known_at_ns, u.source_index))
    if not additions:
        reasons.append("no_authoritative_addition")
    if not modifications and snapshot_binding is None:
        reasons.append("a_only_no_authoritative_modification")
    if snapshot_binding is not None:
        expected_binding = {
            "semantics": SNAPSHOT_SEMANTICS, "dataset": "GLBX.MDP3",
            "publisher": publisher, "symbol": "NQ.c.0", "schema": "definition",
            "provider_documentation": SNAPSHOT_DOC, "export_documentation": QUANTPAD_DOC,
        }
        if (not isinstance(snapshot_binding, Mapping)
                or any(snapshot_binding.get(k) != v for k, v in expected_binding.items())):
            reasons.append("snapshot_source_binding_missing_or_incompatible")
        elif any((u.source_path, u.source_sha256) !=
                 (snapshot_binding.get("source_path"), snapshot_binding.get("source_sha256"))
                 or not u.source_sha256 for u in scoped_updates):
            reasons.append("snapshot_source_identity_mismatch")
        if (scoped_actions != {"A"} or len(scoped_updates) < 2
                or any(u.provider_at_ns % 86_400_000_000_000 != 0
                       or datetime.fromtimestamp(u.provider_at_ns // 1_000_000_000,
                                                 tz=timezone.utc).weekday() >= 5
                       or u.event_at_ns > u.provider_at_ns for u in scoped_updates)):
            reasons.append("rows_do_not_match_bound_daily_active_snapshot_stream")
        if any(u.instrument_class != "F" for u in scoped_updates):
            reasons.append("snapshot_instrument_not_outright_future")
        # This field is source metadata, not an invented futures dollar multiplier.
        if len({_canonical_json(u.raw.get("contract_multiplier")) for u in scoped_updates}) != 1:
            reasons.append("snapshot_contract_multiplier_conflict")
    if reasons:
        report = _unresolved(root=root, publisher=publisher, observed_count=len(observed),
                             reason_codes=tuple(reasons), target_instrument_id=target_instrument_id,
                             target_year=target_year, raw_actions=raw_actions)
        return _unresolved_result(report, observed)

    original = additions[0]
    changed_modifications = sorted(
        (u for u in (additions if snapshot_binding is not None else modifications)
         if u.activation_ns != original.activation_ns),
        key=lambda u: (u.known_at_ns, u.source_index),
    )
    if not changed_modifications and snapshot_binding is None:
        reasons.append("no_changed_modification_authorization")
    authorization = original if snapshot_binding is not None else (changed_modifications[0] if changed_modifications else None)
    if snapshot_binding is None and authorization is not None and authorization.known_at_ns <= original.known_at_ns:
        reasons.append("modification_not_later_than_original")
    earliest_observed = min(start_ns for _, _, start_ns, _ in observed)
    if original.activation_ns > earliest_observed or any(
            update.activation_ns > earliest_observed for update in
            (scoped_updates if snapshot_binding is not None else modifications)):
        reasons.append("activation_not_before_all_observed_2024_dates")
    if reasons:
        report = _unresolved(root=root, publisher=publisher, observed_count=len(observed),
                             reason_codes=tuple(reasons), target_instrument_id=target_instrument_id,
                             target_year=target_year, raw_actions=raw_actions)
        return _unresolved_result(report, observed)

    coordinate = original.coordinate
    canonical_payload = {
        "version": NONRETROACTIVE_VERSION,
        "physical_coordinate_id": coordinate.identity,
        "publisher": coordinate.publisher,
        "publisher_id": coordinate.publisher_id,
        "original_source_path": original.source_path,
        "original_source_sha256": original.source_sha256,
        "original_activation_ns": original.activation_ns,
        "authorization_known_at_ns": authorization.known_at_ns,
        "authorization_source_path": authorization.source_path,
        "authorization_source_sha256": authorization.source_sha256,
        "authorization_source_row": authorization.source_row,
    }
    if snapshot_binding is not None:
        canonical_payload["snapshot_binding"] = dict(snapshot_binding)
    candidate_version = f"{NONRETROACTIVE_VERSION}:{_digest(canonical_payload)}"
    candidate_rows = []
    pre_known_rows = []
    expiry_excluded_rows = []
    selected_versions: dict[str, int] = {}
    for _, row, start_ns, _ in observed:
        if start_ns < authorization.known_at_ns:
            pre_known_rows.append(dict(row))
            continue
        end_ns = _observed_end(row, start_ns)
        if start_ns >= coordinate.expiration_ns or end_ns > coordinate.expiration_ns:
            expiry_excluded_rows.append(dict(row))
            continue
        try:
            selected = _latest_known_compatible_update(scoped_updates, coordinate, start_ns)
        except SupersessionInputError:
            reasons.append("same_known_at_compatible_bar_conflict")
            continue
        if selected is None:
            reasons.append("no_known_compatible_update_at_bar")
            continue
        retained_version, version_source = _retained_definition_version(selected)
        selected_versions[selected.definition_version or retained_version] = selected.known_at_ns
        candidate_rows.append({
            "original": dict(row),
            "candidate_definition": {
                "definition_version": retained_version,
                "latest_known_definition_version": selected.definition_version,
                "definition_version_source": version_source,
                "contract_key": original.contract_key,
                "original_contract_key": original.contract_key,
                "selected_definition_contract_key": selected.contract_key,
                "physical_coordinate_id": coordinate.identity,
                "physical_coordinate_version": PHYSICAL_COORDINATE_VERSION,
                "supersession_known_at_ns": selected.known_at_ns,
                "authorization_known_at_ns": authorization.known_at_ns,
                "latest_known_activation_ns": selected.activation_ns,
                "original_activation_ns": original.activation_ns,
                "expiration_ns": coordinate.expiration_ns,
                "nonretroactive": True,
                "price_readmission_pending": True,
                "matched_original_columns": tuple(row.keys()),
                "matched_original_values_sha256": _row_digest(row),
                "source_update": selected.as_dict(),
            },
        })
    if reasons:
        report = _unresolved(root=root, publisher=publisher, observed_count=len(observed),
                             reason_codes=tuple(reasons), target_instrument_id=target_instrument_id,
                             target_year=target_year, raw_actions=raw_actions)
        return _unresolved_result(report, observed)
    status = SOURCE_SUPERSESSION_STATUS
    coordinate_publisher_ids = {update.coordinate.publisher_id for update in scoped_updates}
    if coordinate_publisher_ids == {publisher_id}:
        publisher_id_resolution = "raw_field"
    elif coordinate_publisher_ids == {None}:
        publisher_id_resolution = "publisher_namespace_only_raw_field_absent"
    else:
        publisher_id_resolution = "mixed_raw_field_presence"
    report = {
        "schema": SUPPLEMENT_VERSION,
        "status": status,
        "original_status": status,
        "actual_status": "pending_source_wrapper",
        "actual_accepted": False,
        "root": root,
        "publisher": publisher,
        "publisher_id": coordinate.publisher_id,
        "publisher_id_expected": publisher_id,
        "publisher_id_resolution": publisher_id_resolution,
        "target_year": target_year,
        "target_instrument_id": target_instrument_id,
        "target_symbol": target_symbol,
        "raw_actions": tuple(raw_actions),
        "target_year_end_ns": TARGET_YEAR_END_NS,
        "future_definition_rows_excluded_from_conflict_scope": len(future_updates),
        "future_definition_known_at_scope": "known_at_ns <= target_year_end_ns",
        "future_definition_rows_affect_candidates": False,
        "receipt_selection": {
            "policy": "known_at_ns=max(t,ts_recv)+250ms",
            "latency_ns": DEFAULT_LATENCY_NS,
            "authoritative_original": {
                "event_at_ns": original.event_at_ns,
                "provider_at_ns": original.provider_at_ns,
                "chosen_receipt_ns": max(original.event_at_ns, original.provider_at_ns),
                "known_at_ns": original.known_at_ns,
            },
            "authoritative_modification": {
                "event_at_ns": authorization.event_at_ns,
                "provider_at_ns": authorization.provider_at_ns,
                "chosen_receipt_ns": max(authorization.event_at_ns, authorization.provider_at_ns),
                "known_at_ns": authorization.known_at_ns,
            },
        },
        "authoritative_original": original.as_dict(),
        "authoritative_modification": authorization.as_dict(),
        "changed_modifications": tuple(update.as_dict() for update in changed_modifications),
        "physical_coordinate": coordinate.as_dict(),
        "source_namespace": {
            "publisher": publisher,
            "publisher_id": coordinate.publisher_id,
            "source_path": original.source_path,
            "source_sha256": original.source_sha256,
            "all_scoped_updates_same_namespace": True,
            "binding": "publisher plus retained source path/hash",
        },
        "earliest_known_physical_coordinate": {
            "known_at_ns": original.known_at_ns,
            "source_path": original.source_path,
            "source_row": original.source_row,
            "raw_fields_sha256": original.raw_fields_sha256,
            "definition_version": original.definition_version,
            "identity": coordinate.identity,
        },
        "candidate_supersession_version": candidate_version,
        "nonretroactive": True,
        "supersession_known_at_ns": authorization.known_at_ns,
        "observed_count": len(observed),
        "candidate_count": len(candidate_rows),
        "corrected_count": 0,
        "pre_known_count": len(pre_known_rows),
        "expiry_excluded_count": len(expiry_excluded_rows),
        "activation_before_all_observed_2024_dates": True,
        "latest_known_versions": dict(selected_versions),
        "price_readmission_pending": True,
        "generic_admission_untouched": True,
        "actual_validation_stage": "registered_check7_extract8",
        "dbn_instrument_definition_docs": DBN_INSTRUMENT_DEF_DOC,
    }
    if snapshot_binding is not None:
        report.update(schema="jumbo-nq2024-definition-snapshot-supplement-v2",
                      source_semantics=SNAPSHOT_SEMANTICS,
                      snapshot_binding=dict(snapshot_binding),
                      authoritative_snapshot=report.pop("authoritative_modification"),
                      changed_snapshot_states=report.pop("changed_modifications"),
                      actual_validation_stage="registered_worker_with_bound_snapshot_contract",
                      snapshot_interpretation="active point-in-time source state; latest already known receipt; original A action retained",
                      availability_limit="Synthetic daily snapshot timestamp plus the declared 250ms latency scenario, not measured historical delivery latency")
        report["receipt_selection"]["authoritative_snapshot"] = report["receipt_selection"].pop("authoritative_modification")
    return {"report": report,
            "candidate_canonical2024": tuple(candidate_rows),
            "corrected_canonical2024": (),
            "pre_known_rows": tuple(pre_known_rows),
            "expiry_excluded_rows": tuple(expiry_excluded_rows)}


def _source_entry(definition_source: Mapping[str, Any] | str | Path,
                  source_protocol: Mapping[str, Any]) -> tuple[Path, str, str, int | None, int | None]:
    if isinstance(definition_source, Mapping):
        entry = dict(definition_source)
    else:
        entry = {"source_path": str(definition_source)}
    source_name = entry.get("source_path") or entry.get("path")
    if not isinstance(source_name, str) or not source_name:
        raise SupersessionInputError("definition source path is required")
    metadata = source_protocol.get("source_file_metadata", ())
    found: Mapping[str, Any] | None = None
    if isinstance(metadata, Mapping):
        value = metadata.get(source_name)
        if isinstance(value, Mapping):
            found = value
    elif isinstance(metadata, Sequence) and not isinstance(metadata, (str, bytes)):
        for value in metadata:
            if isinstance(value, Mapping) and value.get("path", value.get("source_path")) == source_name:
                found = value
                break
    if found is not None:
        entry = {**dict(found), **entry}
    data_root_value = source_protocol.get("data_root")
    if data_root_value is None:
        raise SupersessionInputError("definition source protocol requires data_root")
    data_root = Path(data_root_value).resolve()
    source = Path(source_name)
    if not source.is_absolute():
        source = data_root / source
    source = source.resolve()
    if not source.is_relative_to(data_root) or source.is_relative_to(Path("/workspace/archive").resolve()):
        raise SupersessionInputError("definition source must remain inside data_root and outside archive")
    if source.suffix != ".parquet":
        raise SupersessionInputError("definition source must be a completed parquet file")
    expected_hash = entry.get("source_sha256", entry.get("sha256"))
    if not isinstance(expected_hash, str) or not expected_hash:
        raise SupersessionInputError("definition source protocol requires a source_sha256")
    expected_size = entry.get("size_bytes")
    if expected_size is not None:
        expected_size = _exact_int(expected_size, "definition source size", positive=True)
    expected_mtime_ns = entry.get("mtime_ns")
    if expected_mtime_ns is not None:
        expected_mtime_ns = _exact_int(expected_mtime_ns, "definition source mtime_ns")
    return source, source_name, expected_hash, expected_size, expected_mtime_ns


def _canonical_records(canonical_ref: Mapping[str, Any] | None) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(canonical_ref, Mapping):
        return ()
    manifest = canonical_ref.get("manifest")
    if isinstance(manifest, Mapping):
        canonical_ref = manifest
    records = canonical_ref.get("records", ())
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        return ()
    return tuple(record for record in records if isinstance(record, Mapping))


def _canonical_source_file(canonical_ref: Mapping[str, Any] | None, source_path: str) -> Mapping[str, Any] | None:
    if not isinstance(canonical_ref, Mapping):
        return None
    manifest = canonical_ref.get("manifest")
    if isinstance(manifest, Mapping):
        canonical_ref = manifest
    files = canonical_ref.get("files", ())
    if isinstance(files, Sequence) and not isinstance(files, (str, bytes)):
        for value in files:
            if isinstance(value, Mapping) and value.get("source_path") == source_path:
                return value
    return None


def _canonical_record(canonical_ref: Mapping[str, Any] | None,
                      source_path: str, source_row: int) -> Mapping[str, Any] | None:
    for record in _canonical_records(canonical_ref):
        if record.get("source_path") == source_path and record.get("source_row") == source_row:
            return record
    return None


def actual_definition_supersession_audit(
    definition_source: Mapping[str, Any] | str | Path,
    source_protocol: Mapping[str, Any],
    canonical_ref: Mapping[str, Any] | None,
    *,
    root: str = TARGET_ROOT,
    publisher: str = "quantpad",
    expected_publisher_id: int = TARGET_PUBLISHER_ID,
    maximum_file_bytes: int = MAX_DEFINITION_AUDIT_BYTES,
) -> dict[str, Any]:
    """Audit one complete raw definition source before any OHLC reread.

    This is deliberately a worker-only boundary.  It uses the registered path
    and hash protocol, reads one complete source bounded to 16 MiB, and joins
    each target raw row to the retained validated definition-index manifest.
    It returns the exact A/M/action counts and relevant source fields for the
    target; it never changes the generic index.
    """
    if (root != TARGET_ROOT or publisher != "quantpad"
            or type(expected_publisher_id) is not int
            or expected_publisher_id != TARGET_PUBLISHER_ID):
        raise SupersessionInputError("definition audit is frozen to the registered NQ/quantpad publisher")
    protocol_publisher_id = source_protocol.get("publisher_id")
    if (protocol_publisher_id is not None
            and (type(protocol_publisher_id) is not int
                 or protocol_publisher_id != expected_publisher_id)):
        raise SupersessionInputError("definition source protocol publisher_id contradicts the registered source expectation")
    source, source_name, expected_hash, expected_size, expected_mtime_ns = _source_entry(
        definition_source, source_protocol
    )
    maximum_file_bytes = _exact_int(maximum_file_bytes, "maximum_file_bytes", positive=True)
    if maximum_file_bytes > MAX_DEFINITION_AUDIT_BYTES:
        raise SupersessionInputError("definition audit exceeds the 16 MiB registered bound")
    try:
        stat = source.stat()
        if stat.st_size > maximum_file_bytes:
            raise SupersessionInputError("definition source exceeds the 16 MiB registered bound")
        if expected_size is not None and stat.st_size != expected_size:
            raise SupersessionInputError("definition source size differs from the registered protocol")
        if expected_mtime_ns is not None and stat.st_mtime_ns != expected_mtime_ns:
            raise SupersessionInputError("definition source mtime differs from the registered protocol")
        payload = source.read_bytes()
    except OSError as exc:
        raise SupersessionInputError("definition source cannot be read as a complete file") from exc
    if len(payload) != stat.st_size or len(payload) > maximum_file_bytes:
        raise SupersessionInputError("definition source changed or exceeded its complete-read bound")
    actual_hash = hashlib.sha256(payload).hexdigest()
    if actual_hash != expected_hash:
        raise SupersessionInputError("definition source hash differs from the registered protocol")
    try:
        import pyarrow as pa
        import pyarrow.ipc as ipc
        import pyarrow.parquet as pq

        parquet = pq.ParquetFile(pa.BufferReader(payload))
        missing = sorted(RAW_AUDIT_REQUIRED_FIELDS - set(parquet.schema_arrow.names))
        if missing:
            raise SupersessionInputError(f"definition source omits required fields: {missing}")
        raw_schema_has_publisher_id = "publisher_id" in parquet.schema_arrow.names
        source_rows = int(parquet.metadata.num_rows)
        table = parquet.read()
        if table.num_rows != source_rows:
            raise SupersessionInputError("definition footer row count differs from complete source read")
        source_schema_sha256 = hashlib.sha256(
            parquet.schema_arrow.serialize().to_pybytes()
        ).hexdigest()
        sink = pa.BufferOutputStream()
        with ipc.new_stream(sink, table.schema) as writer:
            writer.write_table(table)
        all_row_ipc_sha256 = hashlib.sha256(sink.getvalue().to_pybytes()).hexdigest()
        rows = table.to_pylist()
        parquet.close()
    except SupersessionInputError:
        raise
    except Exception as exc:
        raise SupersessionInputError("complete definition source cannot be decoded") from exc

    canonical_file = _canonical_source_file(canonical_ref, source_name)
    issues: list[str] = []
    if canonical_file is None:
        issues.append("canonical_source_file_missing")
    else:
        if canonical_file.get("source_sha256") != actual_hash:
            issues.append("canonical_source_hash_mismatch")
        retained_identity = {
            "size_bytes": len(payload),
            "source_rows": source_rows,
            "schema_sha256": source_schema_sha256,
            "all_row_ipc_sha256": all_row_ipc_sha256,
        }
        for field, actual in retained_identity.items():
            if field in canonical_file and canonical_file.get(field) != actual:
                issues.append(f"canonical_{field}_mismatch")
    # The canonical manifest is the retained admission identity.  A mismatch
    # must stop before target rows can be handed to the candidate builder.
    canonical_identity_issues = tuple(dict.fromkeys(issues))
    if canonical_identity_issues:
        raise SupersessionInputError(
            "definition source differs from retained canonical identity: "
            + ",".join(canonical_identity_issues)
        )
    target_rows: list[dict[str, Any]] = []
    target_publisher_field_presence: list[bool] = []
    action_counts: dict[str, int] = {}
    relevant_fields: list[dict[str, Any]] = []
    for ordinal, raw in enumerate(rows):
        if not isinstance(raw, Mapping) or raw.get("instrument_id") != TARGET_INSTRUMENT_ID:
            continue
        row = dict(raw)
        target_publisher_field_presence.append("publisher_id" in row)
        action: str | None
        try:
            action = _text_enum(row.get("security_update_action"), "security_update_action")
        except SupersessionInputError:
            action = None
            issues.append(f"target_row_{ordinal}_unknown_action")
        action_counts[str(action)] = action_counts.get(str(action), 0) + 1
        try:
            instrument_class = _text_enum(row.get("instrument_class"), "instrument_class")
            if instrument_class != TARGET_INSTRUMENT_CLASS:
                raise SupersessionInputError("target definition is not an outright future")
            security_type = _text_enum(row.get("security_type"), "security_type")
            if security_type is not None and security_type != TARGET_SECURITY_TYPE:
                raise SupersessionInputError("target definition security_type is not futures")
            actual_publisher_id = row.get("publisher_id")
            if ("publisher_id" in row and actual_publisher_id is not None
                    and (type(actual_publisher_id) is not int
                         or actual_publisher_id != expected_publisher_id)):
                raise SupersessionInputError("target definition publisher_id differs from registered CME publisher")
            if row.get("raw_symbol") != TARGET_SYMBOL:
                raise SupersessionInputError("target definition raw_symbol differs from NQZ4")
        except SupersessionInputError as exc:
            issues.append(f"target_row_{ordinal}_{type(exc).__name__}")
        row.update({
            "root": root,
            "publisher": publisher,
            "publisher_id": row.get("publisher_id"),
            "source_path": source_name,
            "source_row": ordinal,
            "source_sha256": actual_hash,
        })
        record = _canonical_record(canonical_ref, source_name, ordinal)
        if record is None:
            issues.append(f"target_row_{ordinal}_canonical_record_missing")
        else:
            if record.get("source_sha256") != actual_hash:
                issues.append(f"target_row_{ordinal}_canonical_hash_mismatch")
            for field in ("contract_key", "definition_version", "raw_fields_sha256"):
                if record.get(field) is None:
                    issues.append(f"target_row_{ordinal}_canonical_{field}_missing")
                else:
                    row[field] = record[field]
        target_rows.append(row)
        relevant_fields.append({
            key: row.get(key) for key in (
                "source_path", "source_row", "source_sha256", "security_update_action",
                "publisher_id", "instrument_class", "security_type", "instrument_id",
                "raw_symbol", "activation", "expiration", "min_price_increment", "t",
                "ts_recv", "contract_key", "definition_version", "raw_fields_sha256",
            )
        })
    target_publisher_ids = {
        row.get("publisher_id") for row in target_rows
        if type(row.get("publisher_id")) is int
    }
    all_target_rows_have_publisher_id = bool(target_rows) and all(
        target_publisher_field_presence
    ) and all(type(row.get("publisher_id")) is int for row in target_rows)
    if all_target_rows_have_publisher_id and len(target_publisher_ids) == 1:
        publisher_id_source = "raw_field"
        observed_publisher_id = next(iter(target_publisher_ids))
        publisher_id_unresolved = ()
    elif any(target_publisher_field_presence):
        publisher_id_source = "mixed_or_invalid_raw_field"
        observed_publisher_id = None
        publisher_id_unresolved = ("publisher_id_not_resolved_for_all_target_rows",)
    else:
        publisher_id_source = "raw_field_absent"
        observed_publisher_id = None
        publisher_id_unresolved = ("publisher_id_missing_from_raw_source",)
    report = {
        "schema": "jumbo-definition-supersession-raw-audit-v1",
        "status": "audited" if not issues else "unresolved",
        "source_path": source_name,
        "source_sha256": actual_hash,
        "source_bytes": len(payload),
        "source_rows": source_rows,
        "schema_sha256": source_schema_sha256,
        "source_schema_sha256": source_schema_sha256,
        "all_row_ipc_sha256": all_row_ipc_sha256,
        "raw_schema_has_publisher_id": raw_schema_has_publisher_id,
        "target_row_count": len(target_rows),
        "target_action_counts": dict(sorted(action_counts.items())),
        "target_a_count": action_counts.get("A", 0),
        "target_m_count": action_counts.get("M", 0),
        "target_relevant_fields": tuple(relevant_fields),
        "issues": tuple(dict.fromkeys(issues)),
        "unresolved_factors": publisher_id_unresolved,
        "canonical_source_file": dict(canonical_file) if canonical_file is not None else None,
        "maximum_file_bytes": maximum_file_bytes,
        "publisher_id": observed_publisher_id,
        "publisher_id_expected": expected_publisher_id,
        "publisher_id_source": publisher_id_source,
        "generic_admission_untouched": True,
        "dbn_instrument_definition_docs": DBN_INSTRUMENT_DEF_DOC,
    }
    return {"report": report, "definition_rows": tuple(target_rows)}


def _read_store_json(store: Any, value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        if isinstance(value.get("manifest"), Mapping):
            return value
        if "records" in value or "files" in value:
            return value
    if store is None or value is None or not hasattr(store, "read_json"):
        return None
    try:
        from trading_research.operations.artifacts import artifact_ref
        return store.read_json(artifact_ref(value))
    except Exception:
        try:
            return store.read_json(value)
        except Exception:
            return None


def _protocol_metadata(protocol: Mapping[str, Any], source_path: str,
                       canonical_ref: Mapping[str, Any] | None = None) -> dict[str, Any]:
    metadata = protocol.get("source_file_metadata", ())
    result: dict[str, Any] = {"source_path": source_path}
    if isinstance(metadata, Mapping):
        value = metadata.get(source_path)
        if isinstance(value, Mapping):
            result.update(dict(value))
    elif isinstance(metadata, Sequence) and not isinstance(metadata, (str, bytes)):
        for value in metadata:
            if isinstance(value, Mapping) and value.get("path", value.get("source_path")) == source_path:
                result.update(dict(value))
                break
    result["source_path"] = source_path
    canonical_file = _canonical_source_file(canonical_ref, source_path)
    if isinstance(canonical_file, Mapping):
        for field in ("source_sha256", "size_bytes"):
            retained = canonical_file.get(field)
            configured = result.get(field)
            if retained is not None and configured is not None and configured != retained:
                raise SupersessionInputError(
                    f"protocol {field} differs from retained definition manifest"
                )
            if retained is not None:
                result[field] = retained
    return result


def _definition_source_paths(protocol: Mapping[str, Any], admission: Mapping[str, Any], target_root: str) -> tuple[str, ...]:
    values = protocol.get("definition_source_paths")
    if values is None:
        definitions = admission.get("definitions")
        target_info = definitions.get(target_root) if isinstance(definitions, Mapping) else None
        values = target_info.get("source_files", ()) if isinstance(target_info, Mapping) else ()
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return ()
    selected = []
    for value in values:
        path = value.get("source_path", value.get("path")) if isinstance(value, Mapping) else value
        if isinstance(path, str) and f"__{target_root.lower()}-" in path:
            selected.append(path)
    return tuple(dict.fromkeys(selected))


def _worker_data_root(project_root: Path, protocol: Mapping[str, Any]) -> Path:
    expected = (Path(project_root).resolve().parent / "data").resolve()
    value = protocol.get("data_root")
    if value is None:
        return expected
    configured = Path(value)
    if not configured.is_absolute():
        configured = Path(project_root).resolve() / configured
    configured = configured.resolve()
    if configured != expected:
        raise SupersessionInputError(
            "protocol data_root differs from the registered worker root parent/data"
        )
    return expected


def _probe_report_base(protocol: Mapping[str, Any], admission: Mapping[str, Any], target_root: str) -> dict[str, Any]:
    return {
        "schema": "jumbo-definition-supersession-probe-v1",
        "root": target_root,
        "target_year": TARGET_YEAR,
        "target_instrument_id": TARGET_INSTRUMENT_ID,
        "target_symbol": TARGET_SYMBOL,
        "original_status": admission.get("status", admission.get("scope", "unknown")),
        "actual_status": "unresolved",
        "actual_accepted": False,
        "generic_admission_untouched": True,
        "generic_reader_artifacts_preserved": True,
        "actual_validation_stage": "registered_check7_extract8",
        "protocol_version": protocol.get("version"),
    }


def _probe_failure(base: Mapping[str, Any], reason_codes: Sequence[str], **extra: Any) -> dict[str, Any]:
    report = {**dict(base), "status": "unresolved", "actual_status": "unresolved",
              "actual_accepted": False, "reason_codes": tuple(dict.fromkeys(reason_codes)), **extra}
    return {"report": report, "corrected_table": None}


def run_supersession_probe(store: Any, protocol: Mapping[str, Any], root: Path | str,
                           admission: Mapping[str, Any], *, snapshot_binding: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Run the registered-worker source gate and optional narrow reread.

    The generic definition index and its original 14 admission artifacts are
    read and retained as-is.  The raw 2024 OHLC source is reread only after a
    complete bounded raw-definition audit proves the selected update or bound
    daily-active-snapshot interpretation. Custom
    resolution is then applied only to target rows whose generic quality reason
    is exactly ``ambiguous_definition``; all other rows and fields must remain
    byte/value-equivalent.  The returned table is pending price readmission and
    is never published by this helper.
    """
    if not isinstance(protocol, Mapping) or not isinstance(admission, Mapping):
        raise SupersessionInputError("probe requires mapping protocol and admission")
    target_root = str(protocol.get("root", TARGET_ROOT)).upper()
    base = _probe_report_base(protocol, admission, target_root)
    if target_root != TARGET_ROOT:
        return _probe_failure(base, ("target_root_mismatch",))
    # The frozen protocol predates this supplementary source gate and has no
    # publisher identity field.  If a caller supplies one, it is only a
    # consistency check; the expected CME publisher_id=1 remains a registered
    # supplement and must still be verified in every raw target row.
    if (protocol.get("publisher_id") is not None
            and (type(protocol.get("publisher_id")) is not int
                 or protocol.get("publisher_id") != TARGET_PUBLISHER_ID)):
        return _probe_failure(base, ("protocol_publisher_id_invalid",))
    if protocol.get("publisher") not in (None, "quantpad"):
        return _probe_failure(base, ("protocol_publisher_invalid",))
    project_root = Path(root).resolve()
    try:
        data_root = _worker_data_root(project_root, protocol)
    except SupersessionInputError as exc:
        return _probe_failure(base, ("protocol_data_root_invalid",), error=str(exc))
    definitions = admission.get("definitions")
    definition_info = definitions.get(TARGET_ROOT) if isinstance(definitions, Mapping) else None
    if not isinstance(definition_info, Mapping):
        return _probe_failure(base, ("validated_definition_admission_missing",))
    source_paths = _definition_source_paths(protocol, admission, TARGET_ROOT)
    if not source_paths:
        return _probe_failure(base, ("definition_source_paths_missing",))
    expected_sources = definition_info.get("source_files")
    if isinstance(expected_sources, Sequence) and not isinstance(expected_sources, (str, bytes)):
        expected_names = []
        malformed_expected_source = False
        for value in expected_sources:
            path = value.get("source_path", value.get("path")) if isinstance(value, Mapping) else value
            if not isinstance(path, str) or not path:
                malformed_expected_source = True
                continue
            expected_names.append(path)
        if malformed_expected_source or set(expected_names) != set(source_paths):
            return _probe_failure(base, ("definition_source_set_differs_from_admission",))
    canonical_value = definition_info.get("artifact", definition_info.get("manifest"))
    canonical_ref = _read_store_json(store, canonical_value)
    if canonical_ref is None:
        return _probe_failure(base, ("validated_definition_manifest_unavailable",))
    source_protocol = {
        **dict(protocol),
        "data_root": str(data_root),
    }
    audits = []
    base['raw_definition_audit_attempts'] = []
    base['raw_definition_index_read_files'] = []
    base['raw_ohlc_read_attempts'] = []
    raw_rows: list[Mapping[str, Any]] = []
    try:
        for source_path in source_paths:
            base['raw_definition_audit_attempts'].append(source_path)
            audit = actual_definition_supersession_audit(
                _protocol_metadata(source_protocol, source_path, canonical_ref), source_protocol, canonical_ref,
                root=TARGET_ROOT, publisher="quantpad", expected_publisher_id=TARGET_PUBLISHER_ID,
            )
            audits.append(audit["report"])
            raw_rows.extend(audit["definition_rows"])
    except SupersessionInputError as exc:
        return _probe_failure(base, ("definition_source_audit_failed",), error=str(exc), audits=tuple(audits))
    base["definition_audits"] = tuple(audits)
    base["publisher_id_expected"] = TARGET_PUBLISHER_ID
    base["publisher_id_resolution"] = tuple(
        report.get("publisher_id_source") for report in audits
    )
    base["publisher_id_unresolved_factors"] = tuple(
        factor for report in audits for factor in report.get("unresolved_factors", ())
    )
    aggregate_actions: dict[str, int] = {}
    for audit_report in audits:
        for action, count in audit_report.get("target_action_counts", {}).items():
            aggregate_actions[action] = aggregate_actions.get(action, 0) + int(count)
    base["target_action_counts"] = dict(sorted(aggregate_actions.items()))
    base["target_a_count"] = aggregate_actions.get("A", 0)
    base["target_m_count"] = aggregate_actions.get("M", 0)
    if any(report.get("status") != "audited" for report in audits):
        return _probe_failure(base, ("definition_source_audit_unresolved",), audits=tuple(audits))
    year_start_ns = 1_704_067_200_000_000_000
    source_gate = build_definition_supersession_supplement(
        tuple(raw_rows),
        ({"date": "2024-01-01", "start_ns": year_start_ns,
          "end_ns": year_start_ns + 60_000_000_000, "instrument_id": TARGET_INSTRUMENT_ID},),
        snapshot_binding=snapshot_binding,
    )
    base["candidate_source_status"] = source_gate["report"].get("status")
    if source_gate["report"].get("status") != SOURCE_SUPERSESSION_STATUS:
        return _probe_failure(base, tuple(source_gate["report"].get("reason_codes", ())),
                              audits=tuple(audits), source_gate=source_gate["report"])
    try:
        from trading_research.data.ohlc import read_definition_index, read_ohlc_partition
    except Exception as exc:
        return _probe_failure(base, ("registered_reader_unavailable",), audits=tuple(audits), error=str(exc))
    definition_paths = [data_root / path for path in source_paths]
    resources = protocol.get("resources", {})
    if not isinstance(resources, Mapping):
        return _probe_failure(base, ("resources_metadata_malformed",), audits=tuple(audits))
    maximum_definition_rows = resources.get("maximum_definition_rows_per_root", 12_000)
    try:
        definition_index = admission.get("definition_index")
        if definition_index is None:
            base['raw_definition_index_read_files'] = list(source_paths)
            definition_index = read_definition_index(
                definition_paths, data_root=data_root, root=TARGET_ROOT,
                maximum_rows=maximum_definition_rows,
            )
        if getattr(definition_index, "root", None) != TARGET_ROOT:
            raise SupersessionInputError("validated definition index root differs from NQ")
    except Exception as exc:
        return _probe_failure(base, ("validated_definition_index_failed",), audits=tuple(audits), error=str(exc))
    admitted_partitions = admission.get("partitions", ())
    if (not isinstance(admitted_partitions, Sequence)
            or isinstance(admitted_partitions, (str, bytes))):
        return _probe_failure(base, ("validated_ohlc_admission_missing",), audits=tuple(audits))
    ohlc_paths = protocol.get("ohlc_source_paths")
    if ohlc_paths is None:
        ohlc_paths = tuple(
            value.get("source_path") for value in admitted_partitions
            if isinstance(value, Mapping) and isinstance(value.get("source_path"), str)
        )
    if not isinstance(ohlc_paths, Sequence) or isinstance(ohlc_paths, (str, bytes)):
        return _probe_failure(base, ("ohlc_source_paths_missing",), audits=tuple(audits))
    target_ohlc = next((value for value in ohlc_paths
                        if isinstance(value, str) and value.endswith("/2024.parquet")
                        and "__nq-" in value), None)
    if target_ohlc is None:
        return _probe_failure(base, ("target_2024_ohlc_source_missing",), audits=tuple(audits))
    partition_info = next(
        (value for value in admitted_partitions
         if isinstance(value, Mapping) and value.get("source_path") == target_ohlc),
        None,
    )
    if partition_info is None:
        return _probe_failure(base, ("validated_ohlc_admission_missing",), audits=tuple(audits))
    ohlc_path = Path(target_ohlc)
    if not ohlc_path.is_absolute():
        ohlc_path = data_root / ohlc_path
    ohlc_path = ohlc_path.resolve()
    archive_root = Path("/workspace/archive").resolve()
    if (not ohlc_path.is_relative_to(data_root)
            or ohlc_path.is_relative_to(archive_root)
            or ohlc_path.suffix != ".parquet"):
        return _probe_failure(base, ("ohlc_source_path_outside_data_root",), audits=tuple(audits))
    try:
        base['raw_ohlc_read_attempts'].append(target_ohlc)
        table, generic_manifest = read_ohlc_partition(
            ohlc_path, data_root=data_root, root=TARGET_ROOT,
            definition_index=definition_index,
            maximum_rows=resources.get("maximum_rows_per_ohlc_file", 600_000),
            maximum_file_bytes=resources.get("maximum_file_bytes", 16 * 1024 * 1024),
        )
    except Exception as exc:
        return _probe_failure(base, ("raw_ohlc_reread_failed",), audits=tuple(audits), error=str(exc))
    if not isinstance(generic_manifest, Mapping):
        return _probe_failure(base, ("generic_manifest_malformed",), audits=tuple(audits))
    admitted_source_sha256 = partition_info.get("source_sha256")
    actual_source_sha256 = generic_manifest.get("source_sha256")
    if (not isinstance(admitted_source_sha256, str)
            or admitted_source_sha256 != actual_source_sha256):
        return _probe_failure(base, ("generic_ohlc_source_hash_differs_from_admission",),
                              audits=tuple(audits), generic_manifest=generic_manifest)
    generic_rows = [dict(row) for row in table.to_pylist()]
    observed_rows = tuple({
        "start_ns": row["start_ns"], "end_ns": row["end_ns"],
        "instrument_id": row.get("instrument_id"), "source_row": row.get("source_row"),
    } for row in generic_rows if row.get("instrument_id") == TARGET_INSTRUMENT_ID)
    candidate = build_definition_supersession_supplement(tuple(raw_rows), observed_rows,
                                                        snapshot_binding=snapshot_binding)
    if candidate["report"].get("status") != SOURCE_SUPERSESSION_STATUS:
        return _probe_failure(base, tuple(candidate["report"].get("reason_codes", ())),
                              audits=tuple(audits), source_gate=candidate["report"],
                              generic_manifest=generic_manifest)
    candidate_by_source_row = {
        row["original"].get("source_row"): row for row in candidate["candidate_canonical2024"]
    }
    corrected_rows = []
    changed_indices: list[int] = []
    changed_index_set: set[int] = set()
    skipped_reasons: dict[str, int] = {}
    allowed_changes = {"contract_key", "definition_version", "known_at_ns", "valid", "reasons"}
    for index, row in enumerate(generic_rows):
        corrected = dict(row)
        if row.get("instrument_id") == TARGET_INSTRUMENT_ID:
            source_row = row.get("source_row")
            candidate_row = candidate_by_source_row.get(source_row)
            reasons = str(row.get("reasons") or "")
            if candidate_row is not None and reasons == "ambiguous_definition":
                definition = candidate_row["candidate_definition"]
                if definition.get("definition_version_source") != "retained_latest_known":
                    skipped_reasons["latest_definition_version_missing"] = skipped_reasons.get("latest_definition_version_missing", 0) + 1
                elif row.get("start_ns") >= definition["expiration_ns"] or row.get("end_ns") > definition["expiration_ns"]:
                    skipped_reasons["observed_start_or_end_at_expiry"] = skipped_reasons.get("observed_start_or_end_at_expiry", 0) + 1
                else:
                    corrected.update({
                        "contract_key": definition["original_contract_key"],
                        "definition_version": definition["definition_version"],
                        "known_at_ns": max(row["known_at_ns"], definition["supersession_known_at_ns"]),
                        "valid": True,
                        "reasons": "",
                    })
                    changed_indices.append(index)
                    changed_index_set.add(index)
            elif candidate_row is not None:
                skipped_reasons["non_ambiguous_target_row_preserved"] = skipped_reasons.get("non_ambiguous_target_row_preserved", 0) + 1
        corrected_rows.append(corrected)
    for index, (before, after) in enumerate(zip(generic_rows, corrected_rows)):
        differences = {
            key for key in set(before) | set(after)
            if before.get(key) != after.get(key)
        }
        if index in changed_index_set:
            if not differences.issubset(allowed_changes):
                return _probe_failure(base, ("corrected_row_changed_unowned_columns",), audits=tuple(audits),
                                      generic_manifest=generic_manifest, row=index, differences=tuple(sorted(differences)))
        elif differences:
            return _probe_failure(base, ("generic_row_changed_outside_target_ambiguity",), audits=tuple(audits),
                                  generic_manifest=generic_manifest, row=index, differences=tuple(sorted(differences)))
    corrected_table = None
    if changed_indices:
        try:
            import pyarrow as pa
            corrected_table = pa.Table.from_pylist(corrected_rows, schema=table.schema)
        except Exception as exc:
            return _probe_failure(base, ("corrected_table_build_failed",), audits=tuple(audits), error=str(exc))
    report = {
        **base,
        "status": SOURCE_SUPERSESSION_STATUS,
        "actual_status": SOURCE_SUPERSESSION_STATUS,
        "actual_accepted": False,
        "price_readmission_pending": True,
        "audits": tuple(audits),
        "candidate_report": candidate["report"],
        "generic_manifest": generic_manifest,
        "original_partition_artifacts": {
            key: partition_info.get(key) for key in ("canonical_table", "admission_manifest")
        } if isinstance(partition_info, Mapping) else None,
        "generic_source_path": target_ohlc,
        "generic_source_sha256": generic_manifest.get("source_sha256"),
        "generic_rows": len(generic_rows),
        "corrected_rows": len(changed_indices),
        "corrected_table_available": corrected_table is not None,
        "recover_ambiguous_only": True,
        "changed_row_indices": tuple(changed_indices),
        "skipped_target_rows": dict(sorted(skipped_reasons.items())),
        "generic_rows_unchanged_outside_target_ambiguity": True,
        "generic_admission_artifacts_preserved": True,
        "original_admission_partition_count": len(admitted_partitions),
        "corrected_contract_key_policy": "earliest_known_original_contract_key",
        "corrected_definition_version_policy": "latest_known_retained",
    }
    return {"report": report, "corrected_table": corrected_table}


__all__ = [
    "DBN_INSTRUMENT_DEF_DOC",
    "DEFAULT_LATENCY_NS",
    "DefinitionUpdate",
    "INT64_MAX",
    "MAX_DEFINITION_AUDIT_BYTES",
    "NONRETROACTIVE_VERSION",
    "PHYSICAL_COORDINATE_VERSION",
    "PhysicalCoordinate",
    "OPTIONAL_RAW_AUDIT_FIELDS",
    "RAW_AUDIT_REQUIRED_FIELDS",
    "REGISTERED_DEFINITION_FIELDS",
    "SOURCE_SUPERSESSION_STATUS",
    "SUPPLEMENT_VERSION",
    "SupersessionInputError",
    "TARGET_INSTRUMENT_ID",
    "TARGET_INSTRUMENT_CLASS",
    "TARGET_PUBLISHER_ID",
    "TARGET_ROOT",
    "TARGET_SECURITY_TYPE",
    "TARGET_SYMBOL",
    "TARGET_YEAR",
    "TARGET_YEAR_END_NS",
    "UPDATE_ACTIONS",
    "actual_definition_supersession_audit",
    "build_definition_supersession_supplement",
    "run_supersession_probe",
]
