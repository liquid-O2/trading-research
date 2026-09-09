"""Bounded, explicit E0 interchange; never imports types named by input bytes."""
from dataclasses import fields
from datetime import date
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import stat
from types import MappingProxyType

from trading_research.errors import ContractError, IntegrityError
from trading_research.data.events import CanonicalEvent, Flags, Quote, SourceAddress
from trading_research.data.book import RecoveryCertificate
from trading_research.execution.costs import FeeSchedule
from trading_research.experiments.e0.admission import E0DayAdmission, E0OperationalBinding
from trading_research.experiments.e0.candidates import E0Object, FrozenRange
from trading_research.experiments.e0.cohort import DayCompleteness
from trading_research.experiments.e0.learning import E0BinaryFit, E0BracketRouter, E0Head, E0LearningConfig, E0Stages, e0_stages
from trading_research.experiments.e0.learning_store import E0CommittedBinaryFit, E0ModelBinding
from trading_research.experiments.e0.runner import (
    E0MinutePrice, E0RunDay, E0RunManifest, E0Scenario, e0_run_inputs, validate_run_inputs,
)
from trading_research.experiments.e0.source_bridge import E0FrozenContext, NativeCoverageReceipt
from trading_research.foundations.contracts import Band, InstrumentKey
from trading_research.foundations.instruments import InstrumentDefinition
from trading_research.foundations.time import AvailabilityBasis, Clocks
from trading_research.foundations.units import FuturesTerms, Unit
from trading_research.operations.artifacts import ArtifactRef, ArtifactStore, canonical_json, digest, publish_new
from trading_research.operations.artifact_graph import CommitRef, Limits, SemanticArtifactStore
from trading_research.operations.provenance import InputValue
from trading_research.research.calibration import CalibratedBinary
from trading_research.research.folds import FittedArtifact, Fold, Sample
from trading_research.research.models import BinaryExample, BinaryModel, FrequencyModel
from trading_research.research.period import ResearchScopeV1

_SCHEMA = "E0BundleV1"
_MAX_FILE = 64 * 1024 * 1024
_MAX_TOTAL = 256 * 1024 * 1024
_MAX_FILES = 4096
_CLASSES = (CanonicalEvent, Quote, SourceAddress, RecoveryCertificate, FeeSchedule,
    E0DayAdmission, E0OperationalBinding, E0Object, FrozenRange, DayCompleteness,
    E0BinaryFit, E0BracketRouter, E0Head, E0LearningConfig, E0Stages,
    E0CommittedBinaryFit, E0ModelBinding, E0MinutePrice, E0RunDay, E0RunManifest,
    E0Scenario, E0FrozenContext, NativeCoverageReceipt, Band, InstrumentKey,
    InstrumentDefinition, Clocks, FuturesTerms, ArtifactRef, CommitRef, Limits,
    InputValue, CalibratedBinary, FittedArtifact, Fold, Sample, BinaryExample,
    BinaryModel, FrequencyModel, ResearchScopeV1)
_TYPES = {cls.__name__: cls for cls in _CLASSES}
_ENUMS = {cls.__name__: cls for cls in (Flags, AvailabilityBasis, Unit)}


def _wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _path(root, relative):
    if type(relative) is not str or not relative or "\\" in relative:
        raise IntegrityError("invalid bundle relative path")
    path = PurePosixPath(relative)
    if path.is_absolute() or any(p in ("", ".", "..") for p in relative.split("/")):
        raise IntegrityError("bundle path escapes its root")
    result = root.joinpath(*path.parts)
    for parent in (result, *result.parents):
        if parent.is_symlink():
            raise IntegrityError("bundle paths cannot contain symbolic links")
    return result


def _read(path):
    mode = path.lstat()
    if not stat.S_ISREG(mode.st_mode) or mode.st_size > _MAX_FILE:
        raise IntegrityError("bundle requires bounded regular files")
    with path.open("rb") as stream:
        data = stream.read(_MAX_FILE + 1)
    if len(data) != mode.st_size or len(data) > _MAX_FILE:
        raise IntegrityError("bundle file changed or exceeded its bound")
    return data


def _files(root):
    _path(root, "bundle.json")
    if not root.is_dir():
        raise IntegrityError("bundle root must be an existing directory")
    result = []
    for count, path in enumerate(root.rglob("*"), 1):
        if count > 4 * _MAX_FILES:
            raise IntegrityError("bundle directory entry count exceeded")
        if path.is_symlink():
            raise IntegrityError("bundle cannot contain symbolic links")
        if not path.is_dir():
            result.append(path.relative_to(root).as_posix())
            if len(result) > _MAX_FILES:
                raise IntegrityError("bundle file count exceeded")
    return tuple(sorted(result))


class _Codec:
    def __init__(self, root, exporting=False):
        self.root, self.exporting = root, exporting
        self.stores = {}
        self.nodes = 0
        self.total = 0
        self.file_count = 0

    def count(self, depth):
        self.nodes += 1
        if depth > 64 or self.nodes > 500000:
            raise IntegrityError("bundle typed structure exceeded its bound")

    def encode(self, value, depth=0):
        self.count(depth)
        encode = lambda x: self.encode(x, depth + 1)
        kind = type(value)
        if kind in _ENUMS.values():
            return {"enum": kind.__name__, "value": value.value}
        if value is None or kind in (str, int, bool):
            return value
        if kind is float:
            if not math.isfinite(value):
                raise ContractError("nonfinite bundle number")
            return value
        if kind in (Decimal, Fraction, bytes, date):
            raw = (str(value) if kind is Decimal else [value.numerator, value.denominator]
                   if kind is Fraction else value.hex() if kind is bytes else value.isoformat())
            return {"scalar": kind.__name__, "value": raw}
        if kind in (tuple, list, frozenset):
            items = [encode(x) for x in value]
            if kind is frozenset:
                items.sort(key=_wire)
            return {"sequence": kind.__name__, "items": items}
        if kind in (dict, MappingProxyType):
            return {"mapping": [[encode(k), encode(v)] for k, v in value.items()]}
        if kind is SemanticArtifactStore:
            identity = (str(value.root.resolve()), value.namespace, value.limits)
            if identity not in self.stores:
                relative = "models/store-" + str(len(self.stores))
                self.stores[identity] = relative
                source = value.root.absolute()
                _path(source, "configuration.json")
                if source == self.root or self.root in source.parents or source in self.root.parents:
                    raise ContractError("export root must be separate from model stores")
                for name in _files(source):
                    raw = _read(_path(source, name))
                    self.total += len(raw)
                    self.file_count += 1
                    if self.total > _MAX_TOTAL or self.file_count + 8 > _MAX_FILES:
                        raise IntegrityError("bundle retained bytes exceeded bound")
                    publish_new(_path(self.root, relative + "/" + name), raw)
            return {"store": self.stores[identity], "namespace": value.namespace,
                    "limits": encode(value.limits)}
        if kind in _CLASSES:
            return {"type": kind.__name__, "fields": {f.name: encode(getattr(value, f.name))
                    for f in fields(value) if f.init}}
        raise ContractError("unsupported E0 bundle type: " + kind.__name__)

    def decode(self, value, depth=0):
        self.count(depth)
        decode = lambda x: self.decode(x, depth + 1)
        if value is None or type(value) in (str, int, bool):
            return value
        if type(value) is float and math.isfinite(value):
            return value
        if type(value) is not dict:
            raise IntegrityError("invalid typed bundle value")
        keys = set(value)
        if keys == {"enum", "value"} and value["enum"] in _ENUMS:
            return _ENUMS[value["enum"]](value["value"])
        if keys == {"scalar", "value"}:
            raw, name = value["value"], value["scalar"]
            if name == "Decimal" and type(raw) is str:
                result = Decimal(raw)
                if result.is_finite():
                    return result
            if name == "Fraction" and type(raw) is list and len(raw) == 2 and all(type(x) is int for x in raw):
                return Fraction(*raw)
            if name == "bytes" and type(raw) is str:
                return bytes.fromhex(raw)
            if name == "date" and type(raw) is str:
                return date.fromisoformat(raw)
        if keys == {"sequence", "items"} and type(value["items"]) is list:
            constructors = {"tuple": tuple, "list": list, "frozenset": frozenset}
            if value["sequence"] in constructors:
                return constructors[value["sequence"]](decode(x) for x in value["items"])
        if keys == {"mapping"} and type(value["mapping"]) is list:
            result = {}
            for pair in value["mapping"]:
                if type(pair) is not list or len(pair) != 2:
                    raise IntegrityError("invalid bundle mapping pair")
                key, item = decode(pair[0]), decode(pair[1])
                if key in result:
                    raise IntegrityError("duplicate bundle mapping key")
                result[key] = item
            return result
        if keys == {"type", "fields"} and value["type"] in _TYPES:
            cls = _TYPES[value["type"]]
            if type(value["fields"]) is not dict or set(value["fields"]) != {f.name for f in fields(cls) if f.init}:
                raise IntegrityError("bundle dataclass fields differ from explicit schema")
            return cls(**{k: decode(v) for k, v in value["fields"].items()})
        if keys == {"store", "namespace", "limits"}:
            relative = value["store"]
            if type(relative) is not str or not relative.startswith("models/store-") or "/" in relative[len("models/"):]:
                raise IntegrityError("invalid model store location")
            path = _path(self.root, relative)
            if not _path(path, "configuration.json").is_file():
                raise IntegrityError("retained model store configuration missing")
            limits = decode(value["limits"])
            key = (relative, value["namespace"], limits)
            if key not in self.stores:
                self.stores[key] = SemanticArtifactStore(path, value["namespace"], limits)
            return self.stores[key]
        raise IntegrityError("unknown typed bundle tag")


def _inputs(days, router):
    return e0_run_inputs(days, router)


def _validate(manifest, days, router):
    validate_run_inputs(manifest, days, predict=router)
    for _, heads in router.policies:
        for head in heads:
            if e0_stages(head.fit.stages.population, head.fit.config) != head.fit.stages:
                raise IntegrityError("bundle historical stages differ")
            models = (head.fit.frequency, *head.fit.logistic_candidates, head.fit.selected, head.fit.calibrated)
            for model in {model.id: model for model in models}.values():
                restored = head.committed.binding(model).reopen()
                if canonical_json(restored) != canonical_json(model):
                    raise IntegrityError("bundle fitted model differs from retained F11 bytes")


def _code(raw, expected, verify_code):
    if _sha(raw) != expected:
        raise IntegrityError("retained code hash differs from frozen manifest")
    rows = json.loads(raw)
    if type(rows) is not list or not rows:
        raise IntegrityError("actual code snapshot is missing")
    decoded = []
    for row in rows:
        if type(row) is not list or len(row) != 2 or type(row[0]) is not str or type(row[1]) is not dict or set(row[1]) != {"$bytes"}:
            raise IntegrityError("invalid actual code snapshot")
        name = row[0]
        _path(Path("/"), name)
        if not name.startswith("src/trading_research/") or not name.endswith(".py"):
            raise IntegrityError("code snapshot contains an undeclared path")
        decoded.append((name, bytes.fromhex(row[1]["$bytes"])))
    if tuple(sorted(decoded)) != tuple(decoded) or len({name for name, _ in decoded}) != len(decoded) or canonical_json(tuple(decoded)) != raw:
        raise IntegrityError("code snapshot must retain exact canonical ordered bytes")
    if verify_code:
        repo = Path(__file__).resolve().parents[4]
        actual = tuple((p.relative_to(repo).as_posix(), _read(p)) for p in sorted((repo / "src/trading_research").rglob("*.py")))
        if actual != tuple(decoded):
            raise IntegrityError("installed E0 source differs from the frozen code snapshot")


def write_e0_bundle(root, manifest, days, router, input_artifacts: ArtifactStore):
    """Export actual input bytes and committed stores; performs no fit or replay."""
    root = Path(root).absolute()
    _path(root, "bundle.json")
    if root.exists() and any(root.iterdir()):
        raise ContractError("E0 export requires a new or empty directory")
    if type(input_artifacts) is not ArtifactStore:
        raise ContractError("actual retained input ArtifactStore required")
    _validate(manifest, days, router)
    root.mkdir(parents=True, exist_ok=True)
    retained = {"code_snapshot": manifest.code_hash, **dict(manifest.source_hashes)}
    for name, sha in retained.items():
        if len(sha) != 64 or any(ch not in "0123456789abcdef" for ch in sha):
            raise IntegrityError("invalid retained input SHA256")
        raw = _read(_path(input_artifacts.root.absolute(), sha[:2] + "/" + sha))
        if _sha(raw) != sha:
            raise IntegrityError("retained input bytes changed")
        if name == "code_snapshot":
            _code(raw, manifest.code_hash, True)
        elif raw != canonical_json(_inputs(days, router)[name]):
            raise IntegrityError("retained bytes differ from actual typed input")
        publish_new(_path(root, "inputs/" + name + ".json"), raw)
    payload = _Codec(root, True).encode((manifest, days, router))
    inventory = []
    total = 0
    for name in _files(root):
        raw = _read(_path(root, name))
        total += len(raw)
        inventory.append({"path": name, "sha256": _sha(raw), "size": len(raw)})
    raw = _wire({"schema": _SCHEMA, "inventory": inventory, "payload": payload})
    if len(raw) > _MAX_FILE or total + len(raw) > _MAX_TOTAL:
        raise ContractError("E0 bundle exceeds retained byte bounds")
    publish_new(root / "bundle.json", raw)
    return root / "bundle.json"


def load_e0_bundle(root_or_bundle_path, *, verify_code=True):
    """Verify every retained byte, reconstruct explicit types, and reopen F11."""
    path = Path(root_or_bundle_path).absolute()
    root = path if path.is_dir() else path.parent
    if not path.is_dir() and path.name != "bundle.json":
        raise IntegrityError("bundle entry point must be bundle.json")
    try:
        raw = _read(_path(root, "bundle.json"))
        envelope = json.loads(raw)
        if _wire(envelope) != raw or type(envelope) is not dict or set(envelope) != {"schema", "inventory", "payload"} or envelope["schema"] != _SCHEMA:
            raise IntegrityError("invalid canonical E0 bundle envelope")
        inventory = envelope["inventory"]
        if type(inventory) is not list or len(inventory) >= _MAX_FILES:
            raise IntegrityError("invalid bounded bundle inventory")
        names, total = [], len(raw)
        for item in inventory:
            if type(item) is not dict or set(item) != {"path", "sha256", "size"} or type(item["size"]) is not int:
                raise IntegrityError("invalid bundle inventory entry")
            name = item["path"]
            data = _read(_path(root, name))
            if len(data) != item["size"] or _sha(data) != item["sha256"]:
                raise IntegrityError("retained bundle bytes changed")
            names.append(name)
            total += len(data)
            if total > _MAX_TOTAL:
                raise IntegrityError("bundle retained byte bound exceeded")
        if names != sorted(set(names)) or tuple(sorted((*names, "bundle.json"))) != _files(root):
            raise IntegrityError("bundle inventory differs from actual files")
        result = _Codec(root).decode(envelope["payload"])
        if type(result) is not tuple or len(result) != 3:
            raise IntegrityError("bundle requires manifest, days and router")
        manifest, days, router = result
        _validate(manifest, days, router)
        for name, value in _inputs(days, router).items():
            if _read(_path(root, "inputs/" + name + ".json")) != canonical_json(value):
                raise IntegrityError("retained bundle input differs from decoded values")
        _code(_read(_path(root, "inputs/code_snapshot.json")), manifest.code_hash, verify_code)
        return result
    except (ValueError, TypeError, KeyError, AttributeError, ArithmeticError, RecursionError) as exc:
        raise IntegrityError("malformed typed E0 bundle") from exc


def check_e0_bundle(path):
    manifest, days, router = load_e0_bundle(path)
    return {"success": True, "schema": _SCHEMA, "manifest": manifest.version,
            "scope": manifest.scope, "days": len(days), "cuts": sum(len(day.cuts) for day in days),
            "model_version": router.version, "logical_runs": 64, "fits_performed": 0, "replays_performed": 0}
