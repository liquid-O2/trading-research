"""Versioned source settings and case observations, distinct from market facts.

A figure can identify an observed decision without revealing an exact fill.
Inferred settings are available to explicitly named comparison variants only.
Neither a later publication nor a research annotation is a historical selector.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


CATALOG = Path(__file__).with_name("source_cases_v2.json")
STATES = {"fact", "inference", "unknown", "source_conflict"}


class SourceConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class SourceSetting:
    value: Any
    status: str
    source_refs: tuple[str, ...]
    reason: str

    @classmethod
    def parse(cls, row: dict) -> "SourceSetting":
        if row.get("status") not in STATES:
            raise SourceConfigurationError("setting requires fact/inference/unknown/source_conflict")
        refs = row.get("source_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(x, str) or not x for x in refs):
            raise SourceConfigurationError("setting requires actual source references")
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise SourceConfigurationError("setting requires an evidence explanation")
        if row["status"] == "unknown" and row.get("value") is not None:
            raise SourceConfigurationError("unknown setting cannot contain an assumed value")
        if row["status"] == "fact" and row.get("value") is None:
            raise SourceConfigurationError("a fact must contain the observed value")
        return cls(deepcopy(row.get("value")), row["status"], tuple(refs), row["reason"])

    def resolve(self, *, comparison: bool = False) -> Any:
        if self.status == "fact" or (comparison and self.status == "inference"):
            return deepcopy(self.value)
        return None


def load_catalog(path: Path = CATALOG, *, verify_sources: bool = False) -> dict:
    doc = json.loads(Path(path).read_text())
    if doc.get("schema") != "phase1-source-cases-v2":
        raise SourceConfigurationError("unsupported source-case schema")
    sources, configurations, cases = doc["sources"], doc["configurations"], doc["cases"]
    for key, source in sources.items():
        p = Path(source["path"])
        if not isinstance(source.get("pages"), int) or source["pages"] <= 0:
            raise SourceConfigurationError(f"invalid source page count: {key}")
        if verify_sources and (not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != source["sha256"]):
            raise SourceConfigurationError(f"source changed or missing: {key}")
    for cid, configuration in configurations.items():
        if configuration["configuration_id"] != cid or not configuration.get("version"):
            raise SourceConfigurationError("configuration identity/version mismatch")
        if not configuration.get("author") or not configuration.get("scope"):
            raise SourceConfigurationError("configuration needs author and explicit scope")
        for row in configuration["settings"].values():
            setting = SourceSetting.parse(row)
            for ref in setting.source_refs:
                source_id, page = ref.rsplit(":", 1)
                if source_id not in sources or not 1 <= int(page) <= sources[source_id]["pages"]:
                    raise SourceConfigurationError(f"invalid source page: {ref}")
    if len({c["case_id"] for c in cases}) != len(cases):
        raise SourceConfigurationError("duplicate source case")
    for case in cases:
        for cid in case["configuration_ids"]:
            if cid not in configurations:
                raise SourceConfigurationError(f"unknown case configuration: {cid}")
        for name in ("date", "instrument", "timeframe", "observation_interval", "observed_decision"):
            SourceSetting.parse(case[name])
        if case["evidence_mode"] not in {"source_illustration", "native_control", "synthetic_fixture"} or case["historical_candidate"] is not False:
            raise SourceConfigurationError("retrospective source cases cannot be historical candidates")
        if not case.get('source_images') or case.get('contemporaneous_process_record') is not False:
            raise SourceConfigurationError('case needs an original image reference and honest record timing')
        for image in case['source_images']:
            source = sources.get(image.get('source_key'))
            if source is None or image.get('sha256') != source['sha256'] or not 1 <= image.get('page',0) <= source['pages']:
                raise SourceConfigurationError('source image identity or page mismatch')
        if "later_annotations" not in case or "profiles" not in case:
            raise SourceConfigurationError("source case must retain profiles and later annotations")
        if not case.get("missing_fields") and case["observed_decision"]["status"] == "unknown":
            raise SourceConfigurationError("missing observed decision must be accounted for")
    return deepcopy(doc)


def configuration(config_id: str, *, author: str, comparison: bool = False) -> dict:
    doc = load_catalog()
    cfg = doc["configurations"][config_id]
    if cfg["author"] != author:
        raise SourceConfigurationError("another author's settings cannot supply this method")
    return {"configuration_id": config_id, "version": cfg["version"], "author": author,
            "scope": deepcopy(cfg["scope"]),
            "settings": {k: SourceSetting.parse(v).resolve(comparison=comparison)
                         for k, v in cfg["settings"].items()},
            "setting_evidence": deepcopy(cfg["settings"]),
            "variant": "comparison" if comparison else "source"}


def case_record(case_id: str) -> dict:
    return next(c for c in load_catalog()["cases"] if c["case_id"] == case_id)
