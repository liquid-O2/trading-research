"""Typed empirical populations, deterministic identities, and review hashes."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .protocol import jsonable
from .report import counts

SCHEMA = 'phase1-empirical-v1'


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(jsonable(value), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def content_hash(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(jsonable(value), indent=2, sort_keys=True, allow_nan=False) + '\n'
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(payload)
    temporary.replace(path)
    return sha256(path.read_bytes()).hexdigest()


def implementation_identity(root='/workspace'):
    root = Path(root)
    paths = sorted((root/'implementation/src/trading_research').rglob('*.py'))
    paths += sorted((root/'implementation/src/trading_research/research/method_pack').glob('*.json'))
    paths += [root/'planning/phase-1-live/FORMULAS.md']
    files = {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest() for p in paths}
    return {'sha256': content_hash(files), 'files': files}


@dataclass(frozen=True)
class Opportunity:
    """Immutable information available at the initial population trigger.

    Later endpoint observations belong in ReplayResult. No selected signal,
    private attempt, order or fill is inferred by constructing this record.
    """
    opportunity_id: str
    rule_id: str
    method_id: str
    branch: str
    partition_id: str
    instrument_id: int | str
    session_date: str
    side: str
    occurrence_start: int
    occurrence_end: int
    available_at: int
    reference_id: str
    reference_known_at: int
    reference: dict
    trigger: dict
    expiry_at: int
    assumption_ids: tuple[str, ...]
    registry_sha256: str
    evidence_mode: str = 'research_comparison'
    observation_unit: str = 'market_opportunity'
    actual_selection: None = None
    actual_attempt: None = None
    order_id: None = None
    actual_fill: None = None

    def validate(self):
        if self.evidence_mode != 'research_comparison' or self.observation_unit not in {
                'market_opportunity', 'opening_period_state', 'zone_touch', 'range_path'}:
            raise ValueError('empirical opportunity cannot become a source-faithful trade')
        if self.side not in {'long', 'short'}:
            raise ValueError('market opportunity must retain explicit direction')
        for value in (self.occurrence_start, self.occurrence_end, self.available_at,
                      self.reference_known_at, self.expiry_at):
            if type(value) is not int:
                raise ValueError('opportunity clocks must be int64 nanoseconds')
            if not -(2**63) <= value < 2**63:
                raise ValueError('opportunity clock outside int64')
        point = self.reference.get('initial_event_kind') == 'completion'
        interval_ok = self.occurrence_start == self.occurrence_end if point else self.occurrence_start < self.occurrence_end
        if not interval_ok or not self.reference_known_at <= self.occurrence_start <= self.occurrence_end <= self.available_at <= self.expiry_at:
            raise ValueError('opportunity has unavailable reference or contradictory clocks')
        if not self.assumption_ids or len(set(self.assumption_ids)) != len(self.assumption_ids):
            raise ValueError('comparison must identify its frozen research assumptions')
        if len(self.registry_sha256) != 64:
            raise ValueError('comparison lacks frozen registry identity')
        if any(value is not None for value in (self.actual_selection, self.actual_attempt, self.order_id, self.actual_fill)):
            raise ValueError('market detection cannot manufacture a private trading record')
        if self.trigger.get('known_at') != self.available_at:
            raise ValueError('trigger availability does not match its native snapshot')
        if str(self.trigger.get('instrument_id')) != str(self.instrument_id):
            raise ValueError('trigger instrument differs from opportunity')
        if self.reference.get('reference_id') != self.reference_id:
            raise ValueError('opportunity reference identity mismatch')
        if str(self.reference.get('instrument_id')) != str(self.instrument_id):
            raise ValueError('reference instrument differs from opportunity')
        return self

    def to_dict(self):
        self.validate()
        return jsonable(asdict(self))


@dataclass(frozen=True)
class ReplayResult:
    opportunity_id: str
    verdict: str
    completed_at: int
    endpoint: dict | None
    reason: str
    censored: bool = False
    ambiguous: bool = False
    selected_signal_at: int | None = None
    source_method_verdict: str = 'unknown'
    faithful_disagreements: None = None
    timing_violations: int = 0
    proxy_as_faithful: int = 0

    def validate(self, opportunity: Opportunity):
        opportunity.validate()
        if self.opportunity_id != opportunity.opportunity_id:
            raise ValueError('replay has foreign opportunity identity')
        if self.verdict not in {'pass', 'fail', 'unknown'}:
            raise ValueError('unknown empirical verdict')
        if type(self.completed_at) is not int or not opportunity.available_at <= self.completed_at <= opportunity.expiry_at:
            raise ValueError('replay clocks outside frozen lifecycle')
        if (self.censored or self.ambiguous) and self.verdict != 'unknown':
            raise ValueError('censored or ambiguous endpoint cannot certify a sequence')
        if self.selected_signal_at is not None and (self.verdict != 'pass' or self.selected_signal_at != self.completed_at):
            raise ValueError('comparison signal requires an observed passing endpoint')
        if self.endpoint is not None:
            if self.endpoint.get('known_at') != self.completed_at:
                raise ValueError('endpoint unavailable at replay completion')
            if str(self.endpoint.get('instrument_id')) != str(opportunity.instrument_id):
                raise ValueError('replay endpoint has foreign instrument')
        if self.timing_violations or self.proxy_as_faithful:
            raise ValueError('invalid causal/faithfulness admission')
        return self

    def to_dict(self, opportunity):
        self.validate(opportunity)
        return jsonable(asdict(self))


def population_summary(records):
    """One denominator per opportunity; selected signals are a separate count."""
    rows = list(records)
    ids = [r['opportunity']['opportunity_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate opportunity in empirical denominator')
    out = counts([r['replay']['verdict'] for r in rows])
    out.update(opportunities=len(rows), candidates=len(rows),
               selected_signals=sum(r['replay']['selected_signal_at'] is not None for r in rows),
               actual_selections=None, attempts=None, orders=None, actual_fills=None,
               censored=sum(r['replay']['censored'] for r in rows),
               ambiguous=sum(r['replay']['ambiguous'] for r in rows),
               faithful_disagreements=None,
               timing_violations=sum(r['replay']['timing_violations'] for r in rows),
               proxy_as_faithful=sum(r['replay']['proxy_as_faithful'] for r in rows),
               denominator='All observed initial opportunities, before later sequence confirmation; no actual-trade denominator.')
    if out['N'] != out['opportunities'] or out['n'] != out['p']+out['f']:
        raise ValueError('empirical population counts do not reconcile')
    return out
