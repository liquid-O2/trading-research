"""Actual input reads and complete cache identity, including fitted dependencies."""

from dataclasses import dataclass
from copy import deepcopy
import json
from types import MappingProxyType
from typing import Any, Mapping

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.foundations.time import timestamp


def _identity(value):
    if type(value) is not str or not value:
        raise ContractError("input identity must be a nonempty string")


@dataclass(frozen=True, slots=True)
class InputValue:
    column: str
    version: str
    known_at: int
    payload_json: bytes
    fold_version: str | None = None
    fitted_dependency_ids: tuple[str, ...] = ()
    unavailable_reason: str | None = None

    def __post_init__(self):
        _identity(self.column); _identity(self.version); timestamp(self.known_at)
        if type(self.payload_json) is not bytes:
            raise ContractError("input bytes must be immutable")
        try:
            canonical_json(json.loads(self.payload_json))
        except (ValueError, TypeError, UnicodeError) as exc:
            raise ContractError("input must contain finite JSON") from exc
        if self.fold_version is not None:
            _identity(self.fold_version)
        if self.unavailable_reason is not None:
            _identity(self.unavailable_reason)
        if not isinstance(self.fitted_dependency_ids, tuple):
            raise ContractError("fitted input dependencies must be immutable")
        for id in self.fitted_dependency_ids:
            _identity(id)
        if len(set(self.fitted_dependency_ids)) != len(self.fitted_dependency_ids):
            raise ContractError("duplicate fitted input dependency")


@dataclass(frozen=True, slots=True)
class _AuditConfiguration:
    declared: frozenset[str]
    required: frozenset[str]
    cut: int
    fold_version: str


class InputAudit:
    """Models receive this accessor; declarations are checked against actual reads."""

    __slots__ = ("_configuration", "_values", "_read", "_omissions")

    def __init__(self, declared: frozenset[str], values: Mapping[str, InputValue], *, cut: int,
                 fold_version: str, required: frozenset[str] | None = None):
        required = declared if required is None else required
        if not isinstance(declared, frozenset) or not isinstance(required, frozenset):
            raise ContractError("input declarations must be immutable")
        for name in declared:
            _identity(name)
        timestamp(cut); _identity(fold_version)
        if not required.issubset(declared):
            raise ContractError("required input is absent from the declaration")
        object.__setattr__(self, "_configuration", _AuditConfiguration(declared, required, cut, fold_version))
        object.__setattr__(self, "_values", MappingProxyType(dict(values)))
        if any(not isinstance(value, InputValue) or name != value.column for name, value in self._values.items()):
            raise ContractError("input name and lineage column disagree")
        object.__setattr__(self, "_read", MappingProxyType({}))
        object.__setattr__(self, "_omissions", MappingProxyType({}))

    def __setattr__(self, name, value):
        raise AttributeError("input audit state is immutable")

    def __delattr__(self, name):
        raise AttributeError("input audit state is immutable")

    @property
    def declared(self): return self._configuration.declared

    @property
    def required(self): return self._configuration.required

    @property
    def cut(self): return self._configuration.cut

    @property
    def fold_version(self): return self._configuration.fold_version

    def read(self, column: str) -> bytes:
        if column not in self.declared:
            raise ContractError(f"undeclared model read: {column}")
        value = self._values.get(column)
        if value is None or value.unavailable_reason:
            raise DependencyUnavailable(f"required model input unavailable: {column}")
        if value.known_at > self.cut:
            raise ContractError(f"future-adjusted input read: {column}")
        if value.fold_version is not None and value.fold_version != self.fold_version:
            raise ContractError("incompatible fitted fold input")
        if not value.version:
            raise ContractError("unversioned model input")
        if column in self._omissions:
            raise ContractError("input already explicitly omitted")
        object.__setattr__(self, "_read", MappingProxyType({**self._read, column: value}))
        return value.payload_json

    def omit_optional(self, column, reason):
        _identity(reason)
        if column not in self.declared or column in self.required or column in self._read:
            raise ContractError("only unread declared optional input can be omitted")
        if column in self._omissions and self._omissions[column] != reason:
            raise ContractError("conflicting optional omission")
        object.__setattr__(self, "_omissions", MappingProxyType({**self._omissions, column: reason}))

    def manifest(self) -> dict:
        if self.declared - self._read.keys() - self._omissions.keys():
            raise ContractError("unread optional inputs require explicit omission reason")
        if self.required - self._read.keys():
            raise ContractError(f"registered input omitted from actual model reads: {sorted(self.required - self._read.keys())}")
        reads = {name: {"version": value.version, "known_at": value.known_at,
                        "value_hash": digest(value.payload_json), "fold_version": value.fold_version,
                        "fitted_dependency_ids": list(value.fitted_dependency_ids)}
                 for name, value in sorted(self._read.items())}
        result = {"decision_cut": self.cut, "fold_version": self.fold_version,
                "declared_columns": sorted(self.declared), "actual_reads": reads,
                "unused_optional_columns": sorted(self.declared - self._read.keys())}
        if self._omissions:
            result["optional_omissions"] = dict(self._omissions)
        return result


def cache_key(*, code_hash: str, inputs: Mapping[str, str], target_version: str,
              fold_version: str, transform_versions: tuple[str, ...], model_version: str,
              calibrator_version: str | None, numerical_settings: Mapping[str, Any],
              configuration: Mapping[str, Any]) -> str:
    if not all((code_hash, target_version, fold_version, model_version)) or any(not v for v in inputs.values()):
        raise ContractError("cache identity omits a required dependency version")
    return digest({"code": code_hash, "inputs": dict(inputs), "target": target_version,
                   "fold": fold_version, "transforms": transform_versions, "model": model_version,
                   "calibrator": calibrator_version, "numerical_settings": dict(numerical_settings),
                   "configuration": dict(configuration)})


def compatible_checkpoint(checkpoint: Mapping[str, Any], expected_key: str) -> Mapping[str, Any]:
    if checkpoint.get("cache_key") != expected_key or "state" not in checkpoint:
        raise ContractError("checkpoint belongs to changed input/code/fold/configuration")
    # Reject unsupported/nonfinite values before a checkpoint can be published.
    canonical_json(checkpoint)
    return deepcopy(checkpoint["state"])
