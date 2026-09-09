"""Causal admission and operational gates for the registered E0 harness.

The adapters in this module are intentionally small.  They do not manufacture
calendar, fee, or market-data facts; they bind the already typed foundation
records into one immutable day identity.  Downstream source and replay code can
therefore reject a row by comparing one selected raw instrument/lifetime and
one population scope instead of guessing from a display symbol.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from types import MappingProxyType
from typing import Any, Mapping

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.execution.costs import FeeSchedule
from trading_research.experiments.e0.cohort import (
    DayCompleteness,
    REQUIRED_CHECKS,
)
from trading_research.foundations.cash_calendar import CashDay, VenueBoundary, e0_window
from trading_research.foundations.instruments import InstrumentDefinition, instrument_identity
from trading_research.foundations.rolls import (
    ContractUniverse,
    SessionSequence,
    SessionVolume,
    select_prior_volume,
)
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import FuturesTerms
from trading_research.operations.artifacts import digest


def _text(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise ContractError(f"{label} requires a nonempty identity")
    return value


def _day(value: Any) -> date:
    if type(value) is not date:
        raise ContractError("E0 admission requires an exact civil date")
    return value


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ContractError(f"{label} must be an immutable source manifest mapping")
    return value


def _identity_from_any(value: Any) -> tuple[str, str | None]:
    """Return an instrument ID and optional lifetime from common typed records."""
    if isinstance(value, InstrumentDefinition):
        return value.key.instrument_id, instrument_identity(value)
    if isinstance(value, Mapping):
        iid = value.get("instrument_id", value.get("id"))
        lifetime = value.get("instrument_lifetime", value.get("lifetime"))
        return _text(str(iid) if isinstance(iid, int) else iid, "instrument_id"), lifetime
    if hasattr(value, "key") and hasattr(value.key, "instrument_id"):
        iid = value.key.instrument_id
        return _text(iid, "instrument_id"), getattr(value, "instrument_lifetime", None)
    if hasattr(value, "instrument_id"):
        iid = value.instrument_id
        return _text(str(iid) if isinstance(iid, int) else iid, "instrument_id"), getattr(value, "instrument_lifetime", None)
    if type(value) in (str, int):
        return _text(str(value), "instrument_id"), None
    raise ContractError("downstream source lacks a typed raw instrument identity")


@dataclass(frozen=True)
class E0DayAdmission:
    """One point-in-time selected raw contract and its source readiness row."""

    day: date
    cut: int
    selected_instrument_id: str
    selected_lifetime: str
    selection_version: str
    universe_version: str
    definition_version: str
    prior_session_id: str
    considered: tuple
    excluded: tuple
    selection_evidence: Mapping[str, Any]
    completeness: DayCompleteness
    source_versions: tuple[str, ...]
    scope: str = "E0_historical_2022_2025_harness"
    selected_definition: InstrumentDefinition | None = None

    def __post_init__(self) -> None:
        _day(self.day)
        timestamp(self.cut)
        for value, label in (
            (self.selected_instrument_id, "selected instrument"),
            (self.selected_lifetime, "selected lifetime"),
            (self.selection_version, "selection"),
            (self.universe_version, "universe"),
            (self.definition_version, "definition"),
            (self.prior_session_id, "prior session"),
            (self.scope, "scope"),
        ):
            _text(value, label)
        if type(self.considered) is not tuple or type(self.excluded) is not tuple:
            raise ContractError("admission competitor evidence must be immutable")
        if type(self.completeness) is not DayCompleteness:
            raise ContractError("admission requires one DayCompleteness evidence row")
        if type(self.source_versions) is not tuple or not self.source_versions or any(
                type(v) is not str or not v for v in self.source_versions):
            raise ContractError("admission source versions must be explicit")
        if not isinstance(self.selection_evidence, Mapping):
            raise ContractError("selection evidence must remain inspectable")
        if self.selected_definition is not None:
            if type(self.selected_definition) is not InstrumentDefinition:
                raise ContractError("selected definition must be the typed raw definition")
            if self.selected_definition.key.instrument_id != self.selected_instrument_id:
                raise ContractError("selected definition changed raw instrument identity")
            if instrument_identity(self.selected_definition) != self.selected_lifetime:
                raise ContractError("selected definition changed raw lifetime identity")

    @property
    def version(self) -> str:
        return digest(self)

    @property
    def identity(self) -> tuple[str, str]:
        return self.selected_instrument_id, self.selected_lifetime

    @property
    def day_completeness(self) -> DayCompleteness:
        return self.completeness

    def require_instrument(self, value: Any) -> None:
        iid, lifetime = _identity_from_any(value)
        if iid != self.selected_instrument_id:
            raise ContractError("source changed the admitted raw instrument identity")
        if lifetime is not None and lifetime != self.selected_lifetime:
            raise ContractError("source changed the admitted raw instrument lifetime")

    def require_scope(self, scope: str) -> None:
        if scope != self.scope:
            raise ContractError("historical and primary E0 scopes cannot be joined")


def _manifest_checks(source_manifest: Any) -> tuple[Mapping[str, Any], tuple[str, ...], tuple[str, ...]]:
    manifest = _as_mapping(source_manifest, "source_manifest")
    checks = manifest.get("checks", manifest.get("required_check_states", {}))
    if checks is None:
        checks = {}
    if not isinstance(checks, Mapping):
        raise ContractError("source check states require a mapping")
    versions = manifest.get("data_versions", manifest.get("source_versions", ()))
    if type(versions) is list:
        versions = tuple(versions)
    if type(versions) is not tuple or any(type(v) is not str or not v for v in versions):
        raise ContractError("source versions must be an immutable tuple/list of identities")
    fields = manifest.get("inspected_fields", manifest.get("fields", ()))
    if type(fields) is list:
        fields = tuple(fields)
    if type(fields) is not tuple or any(type(v) is not str or not v for v in fields):
        raise ContractError("inspected source fields must be explicit strings")
    return checks, versions, fields


def _check_state(raw: Any, *, name: str, default: tuple[str, str]) -> tuple[str, str]:
    if raw is None:
        return default
    if isinstance(raw, Mapping):
        state, evidence = raw.get("state"), raw.get("evidence")
    elif type(raw) is tuple and len(raw) == 2:
        state, evidence = raw
    elif type(raw) is str:
        state, evidence = raw, f"source-manifest:{name}"
    else:
        raise ContractError(f"invalid source check record for {name}")
    if state not in ("satisfied", "missing", "invalid", "unassessed") or type(evidence) is not str or not evidence:
        raise ContractError(f"source check {name} needs an explicit state and evidence")
    return state, evidence


def _default_state(name: str, *, universe: ContractUniverse, definition: InstrumentDefinition,
                   selection: Mapping[str, Any], calendar: Any, boundary: Any,
                   source_manifest: Mapping[str, Any]) -> tuple[str, str]:
    direct = {
        "raw_definition": ("satisfied", definition.key.definition_version),
        "product_terms": ("satisfied", definition.key.definition_version),
        "complete_outright_universe": ("satisfied", universe.version),
        "prior_session_volume": ("satisfied", selection.get("preceding_session", selection.get("prior_session", ""))),
    }
    if name == "cash_calendar" and calendar is not None:
        return "satisfied", getattr(calendar, "version", digest(calendar))
    if name == "venue_boundary" and boundary is not None:
        return "satisfied", getattr(boundary, "source_version", digest(boundary))
    return direct.get(name, ("missing", f"source evidence absent:{name}"))


def admit_e0_day(*, day: date, cut: int, universe: ContractUniverse,
                 definitions: tuple[InstrumentDefinition, ...],
                 volumes: tuple[SessionVolume, ...],
                 session_sequence: SessionSequence | None,
                 calendar: Any, boundary: Any, source_manifest: Any,
                 terms: Any, scope: str = "E0_historical_2022_2025_harness") -> E0DayAdmission:
    """Select one raw outright before any labels, outcomes, or P&L are read.

    ``select_prior_volume`` remains the sole selector.  The adapter only adds
    the complete-check row and carries the resulting identity to consumers.
    """
    _day(day)
    timestamp(cut)
    if type(universe) is not ContractUniverse or type(definitions) is not tuple or type(volumes) is not tuple:
        raise ContractError("E0 admission requires typed universe, definitions and volumes")
    if universe.coverage_scope not in ("complete_parent_outrights", "synthetic_complete_parent_fixture"):
        raise DependencyUnavailable("acquired/diagnostic universe is not an exact complete-parent E0 selector")
    if session_sequence is not None and type(session_sequence) is not SessionSequence:
        raise ContractError("session sequence must be the typed venue calendar evidence")
    if type(scope) is not str or not scope:
        raise ContractError("E0 admission scope requires an explicit key")

    # This call is intentionally kept visible at the adapter boundary.  It
    # refuses a missing eligible competitor and preserves every considered row.
    selection = select_prior_volume(
        universe=universe,
        definitions=definitions,
        volumes=volumes,
        previous_session_id=(
            getattr(boundary, "previous_session_id", None)
            or (source_manifest.get("previous_session_id") if isinstance(source_manifest, Mapping) else None)
            or (source_manifest.get("previous_session", {}).get("id") if isinstance(source_manifest, Mapping)
                and isinstance(source_manifest.get("previous_session"), Mapping) else None)
            or (session_sequence.sessions[-2].id if session_sequence is not None else None)
        ),
        cut=cut,
        session_sequence=session_sequence,
    )
    selected_id = str(selection["instrument_id"])
    selected = next((d for d in definitions if d.key.instrument_id == selected_id), None)
    if selected is None:
        raise IntegrityError("volume selector returned a definition outside the supplied universe")
    selected_lifetime = selection.get("instrument_lifetime") or instrument_identity(selected)
    if selected_lifetime != instrument_identity(selected):
        raise IntegrityError("selected lifetime does not match the raw definition")
    if terms is not None:
        supplied_terms = terms.get(selected_id) if isinstance(terms, Mapping) else terms
        if supplied_terms is not None:
            if type(supplied_terms) is not FuturesTerms:
                raise ContractError("selected terms must be typed FuturesTerms")
            if supplied_terms.definition_version != selected.key.definition_version:
                raise ContractError("selected terms changed raw definition identity")
    checks, manifest_versions, inspected_fields = _manifest_checks(source_manifest)
    defaults = {}
    for name in sorted(REQUIRED_CHECKS):
        defaults[name] = _default_state(name, universe=universe, definition=selected,
                                         selection=selection, calendar=calendar, boundary=boundary,
                                         source_manifest=_as_mapping(source_manifest, "source_manifest"))
    check_rows = tuple((name, *_check_state(checks.get(name), name=name, default=defaults[name]))
                       for name in sorted(REQUIRED_CHECKS))
    if not inspected_fields:
        inspected_fields = tuple(sorted({
            "raw_definition", "product_terms", "cash_calendar", "venue_boundary",
            "prior_session_volume", "complete_outright_universe", "mbp_full_schema",
            "book_recovery", "formation_window", "prior_rth_window", "entry_and_label_window",
        }))
    versions = tuple(dict.fromkeys((*manifest_versions, universe.source_version,
                                    selected.key.definition_version, selection["version"],
                                    *(v.source_version for v in volumes),
                                    session_sequence.source_version if session_sequence else "calendar-unbound")))
    completeness = DayCompleteness(day, check_rows, versions, inspected_fields)
    previous_id = selection["preceding_session"]
    evidence = dict(selection)
    evidence["selected_lifetime"] = selected_lifetime
    return E0DayAdmission(
        day=day,
        cut=cut,
        selected_instrument_id=selected_id,
        selected_lifetime=selected_lifetime,
        selection_version=selection["version"],
        universe_version=selection["universe_version"],
        definition_version=selection["definition_version"],
        prior_session_id=previous_id,
        considered=tuple(selection.get("definitions", ())),
        excluded=tuple(sorted(selection.get("excluded", {}).items())),
        selection_evidence=evidence,
        completeness=completeness,
        source_versions=versions,
        scope=scope,
        selected_definition=selected,
    )


def require_selected_identity(admission: E0DayAdmission, value: Any) -> None:
    if type(admission) is not E0DayAdmission:
        raise ContractError("typed E0 day admission required")
    admission.require_instrument(value)


@dataclass(frozen=True)
class E0OperationalBinding:
    day: date
    window: Mapping[str, Any]
    terms: FuturesTerms
    fees: FeeSchedule
    source_versions: tuple[str, ...]
    completeness: DayCompleteness
    period_scope: str
    version: str = ""

    def __post_init__(self) -> None:
        _day(self.day)
        if not isinstance(self.window, Mapping) or not self.window:
            raise ContractError("operational binding needs the frozen E0 window")
        if type(self.terms) is not FuturesTerms or type(self.fees) is not FeeSchedule:
            raise ContractError("operational binding requires typed terms and positive itemized fees")
        if type(self.source_versions) is not tuple or not self.source_versions:
            raise ContractError("operational source versions are required")
        if type(self.completeness) is not DayCompleteness or not self.period_scope:
            raise ContractError("operational completeness/scope evidence is required")
        expected = digest({"day": self.day, "window": self.window, "terms": self.terms,
                           "fees": self.fees, "source_versions": self.source_versions,
                           "completeness": self.completeness, "period_scope": self.period_scope})
        if self.version and self.version != expected:
            raise IntegrityError("operational binding version changed")
        object.__setattr__(self, "version", expected)


def _coverage_check(source_coverage: Any, name: str) -> tuple[str, str]:
    if isinstance(source_coverage, Mapping):
        checks = source_coverage.get("checks", source_coverage)
        value = checks.get(name) if isinstance(checks, Mapping) else None
    else:
        value = getattr(source_coverage, name, None)
    if value is None:
        return "missing", f"source coverage absent:{name}"
    if isinstance(value, Mapping):
        return _check_state(value, name=name, default=("missing", f"source coverage:{name}"))
    if type(value) is bool:
        # A self-declared boolean is not a retained source receipt.  A false
        # value is still useful as an explicit exclusion; true must carry a
        # version/evidence record through a mapping or typed source object.
        if value:
            raise ContractError(f"source coverage {name} needs retained receipt evidence")
        return "missing", f"source coverage:{name}"
    return _check_state(value, name=name, default=("missing", f"source coverage:{name}"))


def bind_e0_day_operational_terms(*, day: date, cash_day: CashDay,
                                  venue_boundary: VenueBoundary, selected_terms: FuturesTerms,
                                  fee_schedule: FeeSchedule, source_coverage: Any,
                                  period_policy: Any, safety_buffer_ns: int,
                                  cut: int | None = None,
                                  require_verified_venue: bool = True) -> E0OperationalBinding:
    """Bind calendar, venue boundary, terms, fees, and source readiness first."""
    _day(day)
    if type(cash_day) is not CashDay or cash_day.day != day:
        raise ContractError("cash calendar row does not match the admitted day")
    if type(venue_boundary) is not VenueBoundary or venue_boundary.day != day:
        raise ContractError("venue boundary row does not match the admitted day")
    if type(selected_terms) is not FuturesTerms or selected_terms.root not in ("NQ", "ES"):
        raise ContractError("selected raw FuturesTerms are required")
    if type(fee_schedule) is not FeeSchedule:
        raise ContractError("positive itemized FeeSchedule is required; zero-fee fallback is forbidden")
    if isinstance(period_policy, Mapping):
        scope = period_policy.get("scope", "")
    else:
        scope = getattr(period_policy, "scope", "")
    if not scope:
        raise ContractError("operational binding requires a named period scope")
    at = cash_day.known_at if cut is None else cut
    timestamp(at)
    window = e0_window(cash_day, boundary=venue_boundary, cut=at,
                       safety_buffer_ns=safety_buffer_ns,
                       require_verified_venue=require_verified_venue)
    checks = {
        "cash_calendar": ("satisfied", cash_day.version),
        "venue_boundary": ("satisfied", digest(venue_boundary)),
        "product_terms": ("satisfied", selected_terms.definition_version),
        "mbp_full_schema": _coverage_check(source_coverage, "mbp_full_schema"),
        "book_recovery": _coverage_check(source_coverage, "book_recovery"),
        "entry_and_label_window": _coverage_check(source_coverage, "entry_and_label_window"),
    }
    # Bind the operational subset; the admission adapter supplies the other
    # exact-universe checks when this row is joined to a day.
    rows = tuple((name, state, evidence) for name, (state, evidence) in sorted(checks.items()))
    # Keep the readiness check's full semantic name in ``checks`` while the
    # disclosed source fields describe the retained entry window itself.  The
    # cohort gate rejects outcome/label fields from eligibility evidence.
    fields = tuple("entry_window" if name == "entry_and_label_window" else name
                   for name in sorted(checks))
    versions = tuple(dict.fromkeys((cash_day.version, digest(venue_boundary),
                                    selected_terms.definition_version, fee_schedule.version,
                                    *(getattr(source_coverage, "source_versions", ())
                                      if not isinstance(source_coverage, Mapping)
                                      else tuple(source_coverage.get("source_versions", ()))))))
    completeness = DayCompleteness(day, rows, versions, fields)
    return E0OperationalBinding(day, window, selected_terms, fee_schedule, versions,
                                completeness, str(scope))


@dataclass(frozen=True)
class ScopeManifest:
    scope: str
    start_date: date
    end_date: date | None
    cohort_version: str
    fold_version: str
    calibration_version: str
    population_version: str

    def __post_init__(self) -> None:
        _text(self.scope, "scope")
        _day(self.start_date)
        if self.end_date is not None:
            _day(self.end_date)
            if self.end_date < self.start_date:
                raise ContractError("scope end precedes scope start")
        for value, label in ((self.cohort_version, "cohort"), (self.fold_version, "fold"),
                             (self.calibration_version, "calibration"), (self.population_version, "population")):
            _text(value, label)

    @property
    def version(self) -> str:
        return digest(self)


@dataclass(frozen=True)
class ScopeBinding:
    historical: ScopeManifest
    primary: ScopeManifest
    version: str = ""

    def __post_init__(self) -> None:
        if type(self.historical) is not ScopeManifest or type(self.primary) is not ScopeManifest:
            raise ContractError("two typed scope manifests are required")
        if self.historical.scope == self.primary.scope:
            raise ContractError("historical and primary scope keys must differ")
        expected = digest((self.historical, self.primary))
        if self.version and self.version != expected:
            raise IntegrityError("scope binding changed after publication")
        object.__setattr__(self, "version", expected)

    def require_same(self, left: str, right: str) -> None:
        if left != right:
            raise ContractError("historical E0 harness cannot silently substitute for the 2020-onward period")


def _coerce_scope(value: Any, default_scope: str) -> ScopeManifest:
    if isinstance(value, ScopeManifest):
        return value
    if not isinstance(value, Mapping):
        raise ContractError("scope input must be ScopeManifest or mapping")
    start = value.get("start_date", value.get("start", "2022-01-01" if "historical" in default_scope else "2020-01-01"))
    end = value.get("end_date", value.get("end"))
    if type(start) is str:
        start = date.fromisoformat(start)
    if type(end) is str:
        end = date.fromisoformat(end)
    return ScopeManifest(
        str(value.get("scope", default_scope)), start, end,
        str(value.get("cohort_version", value.get("cohort", "unpublished-cohort"))),
        str(value.get("fold_version", value.get("folds", "unpublished-folds"))),
        str(value.get("calibration_version", value.get("calibration", "unpublished-calibration"))),
        str(value.get("population_version", value.get("population", "unpublished-population"))),
    )


def separate_scope_manifests(historical_e0_2022_2025: Any,
                             primary_2020_onward: Any) -> ScopeBinding:
    historical = _coerce_scope(historical_e0_2022_2025, "E0_historical_2022_2025_harness")
    primary = _coerce_scope(primary_2020_onward, "primary_model_2020_onward")
    if historical.scope == primary.scope:
        raise ContractError("historical E0 and primary 2020-onward manifests cannot share a scope key")
    return ScopeBinding(historical, primary)


__all__ = [
    "E0DayAdmission", "admit_e0_day", "require_selected_identity",
    "E0OperationalBinding", "bind_e0_day_operational_terms",
    "ScopeManifest", "ScopeBinding", "separate_scope_manifests",
]
