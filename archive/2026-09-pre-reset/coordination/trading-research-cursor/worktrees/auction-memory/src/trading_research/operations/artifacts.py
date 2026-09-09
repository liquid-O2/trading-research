"""Content-addressed files with atomic publication and explicit provenance.

Only the small final directory entry publishes an artifact. Uncommitted temporary
files cannot be read through this API. Original research inputs are never edited.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from types import MappingProxyType
from typing import Any

from trading_research.errors import ContractError, IntegrityError


def json_value(value: Any) -> Any:
    """Preserve exact numerics; refuse lossy arbitrary-object stringification."""
    if isinstance(value, Enum):
        return json_value(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: json_value(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ContractError("nonfinite decimal")
        return {"$decimal": str(value)}
    if isinstance(value, Fraction):
        return {"$fraction": [value.numerator, value.denominator]}
    if isinstance(value, bytes):
        return {"$bytes": value.hex()}
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ContractError("naive datetime has no clock domain")
        return {"$datetime": value.isoformat()}
    if isinstance(value, date):
        return {"$date": value.isoformat()}
    if isinstance(value, (dict, MappingProxyType)):
        if any(not isinstance(k, str) for k in value):
            raise ContractError("JSON keys must be strings")
        return {k: json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted((json_value(v) for v in value), key=canonical_json)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported serialized type: {type(value).__name__}")


def canonical_json(value: Any) -> bytes:
    return json.dumps(json_value(value), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def publish_new(path: Path, payload: bytes) -> None:
    """Never overwrite. Atomic hard-link publication also handles racing writers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != payload:
                raise IntegrityError(f"immutable path already contains other bytes: {path}")
        sync_directory(path.parent)
    finally:
        os.unlink(temporary)


@dataclass(frozen=True)
class ArtifactRef:
    sha256: str
    size_bytes: int
    kind: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise ContractError("invalid artifact SHA-256")
        if type(self.size_bytes) is not int or self.size_bytes < 0 or not self.kind:
            raise ContractError("invalid artifact metadata")


class ArtifactStore:
    def __init__(self, root: Path):
        self.root = Path(root)

    def path(self, ref: ArtifactRef) -> Path:
        return self.root / ref.sha256[:2] / ref.sha256

    def put_bytes(self, payload: bytes, *, kind: str) -> ArtifactRef:
        ref = ArtifactRef(hashlib.sha256(payload).hexdigest(), len(payload), kind)
        publish_new(self.path(ref), payload)
        return ref

    def put_json(self, value: Any, *, kind: str) -> ArtifactRef:
        return self.put_bytes(canonical_json(value), kind=kind)

    def read(self, ref: ArtifactRef) -> bytes:
        payload = self.path(ref).read_bytes()
        if len(payload) != ref.size_bytes or hashlib.sha256(payload).hexdigest() != ref.sha256:
            raise IntegrityError(f"artifact content mismatch: {ref.sha256}")
        return payload

    def read_json(self, ref: ArtifactRef) -> Any:
        return json.loads(self.read(ref))


def artifact_ref(value: dict[str, Any]) -> ArtifactRef:
    return ArtifactRef(**value)


def code_manifest(root: Path) -> dict[str, str]:
    """Hash only this package's code/config; never traverse the excluded archive."""
    paths = list((root / "src").rglob("*.py")) + list((root / "tests").rglob("*.py"))
    paths += sorted((root / "references").rglob("*.py"))
    paths += [p for p in (root / "pyproject.toml", root / "uv.lock") if p.exists()]
    paths += sorted((root / "configs").rglob("*.json"))
    paths += sorted((root / "tests").rglob("*.json"))
    return {str(p.relative_to(root)): file_digest(p) for p in sorted(paths)}


def code_snapshot(root: Path, store: ArtifactStore) -> ArtifactRef:
    """Keep reconstructible source bytes, not just hashes pointing at mutable files."""
    manifest = code_manifest(root)
    files = {name: (root / name).read_bytes() for name in manifest}
    if any(hashlib.sha256(payload).hexdigest() != manifest[name] for name, payload in files.items()):
        raise IntegrityError("code changed while taking its reproducible snapshot")
    return store.put_json({"manifest": manifest, "files": files}, kind="code_snapshot")
