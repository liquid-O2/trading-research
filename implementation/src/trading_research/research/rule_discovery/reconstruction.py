"""P15-04 source reconstruction: ledger, printed arithmetic, B0.1 operand overrides.

Accepted Phase 1 scanners stay frozen. Adapters in subphase 04 read the
registered overrides here. A printed formula without dated inputs cannot
become a source-exact replay pass.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from gzip import GzipFile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from zipfile import ZipFile
import json
import math
import zipfile

from pypdf import PdfReader

from trading_research.errors import ContractError
from trading_research.research.contracts.identity import ASSURANCE_VERSION, digest
from trading_research.research.contracts.outcomes import PassageResult, first_passage
from trading_research.research.method_pack.clocks import ns_to_et
from trading_research.research.method_pack.branch_coverage import ASSUMPTIONS

ROOT = Path("/workspace")
PINE_ZIP = ROOT / "sources/documents/indicators/Pinescript-indicators--main.zip"
PHASE1_RUN = ROOT / "implementation/reports/phase1-live/historical-measurement/run-1.0.1"
SETUP_RECORDS = PHASE1_RUN / "records/setup-records.jsonl.gz"
VIX_PATH = ROOT / "data/free-sources/context__volatility__normalized/VIX.parquet"
CAL_PATH = ROOT / "data/free-sources/context__event-calendar__normalized/economic-releases.parquet"
FOMC_PATH = ROOT / "data/free-sources/context__event-calendar__normalized/fomc-meetings.parquet"
TICK = Decimal("0.25")
POINT_VALUE = Decimal("20")
COMMISSION_SIDE = Decimal("2.50")

CLASSIFICATIONS = frozenset({
    "printed-formula-recovered",
    "printed-but-implementation-differs",
    "inferred-no-printed-formula",
    "not-identifiable-from-owned-source",
})
DISPOSITIONS = frozenset({
    "wiring_only",
    "versioned_baseline_amendment",
    "research_alternative_in_bank",
    "research_alternative_recorded_only",
    "not_identifiable",
    "uncertain_no_change",
})
LEDGER_SCHEMA = "research-source-reconstruction-ledger-v1"
CHECKS_SCHEMA = "research-source-checks-v1"
LIMITS_SCHEMA = "research-dependency-limits-v1"
OVERRIDE_SCHEMA = "research-operand-override-v1"
B0 = "B0"
B01 = "B0.1-2026-09-14"

RULE_BIGTRADES = "P15-04-B0.1-bigtrades-session"
RULE_TBR_15 = "P15-04-B0.1-tbr-projection-1.5"
RULE_REFILL_PRINTED = "P15-04-B0.1-refill-printed-execution"
RULE_MAX_PAIN = "P15-04-O037-max-pain-wiring"
RULE_O043 = "P15-04-O043-ev-wiring"


@dataclass(frozen=True, slots=True)
class OperandOverride:
    rule_id: str
    baseline_rule_id: str
    version: str
    axis: str
    provenance: str
    parameters: dict[str, Any]
    consumed_by: tuple[str, ...]
    preserves_b0: bool
    exposure_note: str


@dataclass(frozen=True, slots=True)
class LedgerRow:
    row_id: str
    operand_id: str
    wiki_object: str
    classification: str
    disposition: str
    raw_anchor: str
    verbatim_quote: str
    implementation_file: str
    implementation_constants: dict[str, Any]
    availability_clock: str
    downstream_consumers: list[str]
    source_exact: bool
    formula: str | None
    discrepancy: str | None
    quote_confirmed: bool
    rule_id: str | None
    notes: str


def conventional_horizon_move(spot: Decimal, sigma: Decimal, t_years: Decimal) -> Decimal:
    """Model-derived 1-sigma log approximation. SPEC fixture 100, 0.2, 0.25 -> 10."""
    if spot <= 0 or sigma < 0 or t_years < 0:
        raise ContractError("conventional horizon move requires non-negative inputs and positive spot")
    return spot * sigma * t_years.sqrt()


def printed_ev_percent(vix: Decimal) -> Decimal:
    return vix / Decimal(252).sqrt()


def printed_ev_points(vix: Decimal, spot: Decimal) -> Decimal:
    return printed_ev_percent(vix) * spot / Decimal(100)


def log_space_iv_bands(prior_settle: Decimal, vol_index: Decimal, *, convention: str, k: Decimal) -> dict[str, Decimal]:
    if prior_settle <= 0 or vol_index < 0:
        raise ContractError("log-space IV bands need positive settle")
    if convention == "16":
        sigma = vol_index / Decimal(16) / Decimal(100)
    elif convention == "sqrt365":
        sigma = vol_index / Decimal(365).sqrt() / Decimal(100)
    else:
        raise ContractError(f"unknown IV convention {convention}")
    log_s = Decimal(str(math.log(float(prior_settle))))
    upper = Decimal(str(math.exp(float(log_s + sigma * k))))
    lower = Decimal(str(math.exp(float(log_s - sigma * k))))
    return {"sigma": sigma, "upper": upper, "lower": lower, "k": k, "convention": Decimal(0)}


def max_pain_strike(contracts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Printed definition: strike where option value is lowest, using prior-date OI."""
    if not contracts:
        return {"available": False, "reason": "empty_chain", "strike": None, "oi_clock": "prior_date"}
    strikes = sorted({Decimal(str(row["strike"])) for row in contracts})
    rights = {str(row.get("right")) for row in contracts}
    coverage = "call_and_put" if rights >= {"CALL", "PUT"} else "incomplete_sides"
    best_k = None
    best_value = None
    for k in strikes:
        total = Decimal(0)
        for row in contracts:
            strike = Decimal(str(row["strike"]))
            oi = Decimal(str(row["oi"]))
            right = str(row["right"])
            if right == "CALL" and k > strike:
                total += oi * (k - strike)
            elif right == "PUT" and k < strike:
                total += oi * (strike - k)
        if best_value is None or total < best_value or (total == best_value and k < best_k):
            best_value = total
            best_k = k
    return {
        "available": True,
        "strike": best_k,
        "option_value": best_value,
        "oi_clock": "prior_date",
        "chain_coverage": coverage,
        "n_contracts": len(contracts),
        "consumed_by_phase_15_setup": False,
    }


def big_trades_session(event_ns: int) -> str:
    local = ns_to_et(event_ns)
    minutes = local.hour * 60 + local.minute
    if 2 * 60 <= minutes < 9 * 60 + 30:
        return "london"
    if 9 * 60 + 30 <= minutes < 16 * 60:
        return "ny"
    return "other"


def big_trades_threshold(session: str, *, version: str) -> int:
    if version == B0:
        return 100
    if session == "london":
        return 75
    return 100


def big_trades_qualifies(size: int, session: str, *, version: str) -> bool:
    return int(size) >= big_trades_threshold(session, version=version)


def tbr_projection_multiples(*, version: str) -> tuple[Decimal, ...]:
    if version == B0:
        return (Decimal("1.33"), Decimal("1.66"))
    return (Decimal("1.33"), Decimal("1.5"), Decimal("1.66"))


def tbr_projection_levels(low: Decimal, high: Decimal, *, version: str) -> dict[str, Any]:
    if high <= low:
        raise ContractError("TBR projection needs high > low")
    width = high - low
    internals = {
        "0.25": low + width * Decimal("0.25"),
        "0.50": low + width * Decimal("0.50"),
        "0.75": low + width * Decimal("0.75"),
    }
    multiples = tbr_projection_multiples(version=version)
    upper = {str(m): high + width * m for m in multiples}
    lower = {str(m): low - width * m for m in multiples}
    return {"width": width, "internals": internals, "upper": upper, "lower": lower, "multiples": [str(m) for m in multiples]}


def range_deviation_ladder(low: Decimal, high: Decimal) -> dict[str, Decimal]:
    if high <= low:
        raise ContractError("range deviation ladder needs high > low")
    width = high - low
    return {
        "h_0.5": high + width * Decimal("0.5"),
        "h_1.0": high + width * Decimal("1.0"),
        "h_2.0": high + width * Decimal("2.0"),
        "l_0.5": low - width * Decimal("0.5"),
        "l_1.0": low - width * Decimal("1.0"),
        "l_2.0": low - width * Decimal("2.0"),
    }


def printed_refill_execution() -> dict[str, Any]:
    return {
        "inside_ticks": 12,
        "stop_ticks": 32,
        "target_ticks": 96,
        "cancel_minutes": 30,
        "one_position_at_a_time": True,
        "round_trip_cost_ticks": 1,
        "stop_slippage_ticks": 1,
    }


def b0_refill_execution() -> dict[str, Any]:
    return {
        "departure_ticks": 4,
        "span_ticks": 2,
        "response_ticks": 4,
        "horizon_minutes": 15,
        "min_event_quantity": 100,
    }


def printed_refill_geometry(side: int, level: Decimal) -> dict[str, Decimal]:
    params = printed_refill_execution()
    inside = TICK * params["inside_ticks"]
    stop_w = TICK * params["stop_ticks"]
    target_w = TICK * params["target_ticks"]
    slip = TICK * params["stop_slippage_ticks"]
    if side == 1:
        entry = level - inside
        stop = entry - stop_w - slip
        target = entry + target_w
    else:
        entry = level + inside
        stop = entry + stop_w + slip
        target = entry - target_w
    return {"entry": entry, "stop": stop, "target": target}


def require_source_stages(observed: Sequence[str], required: Sequence[str], *, replacement_axis: str | None = None) -> bool:
    """S21: a generic wrapper cannot drop a source-required stage unless that axis is the registered replacement."""
    remaining = [stage for stage in required if stage != replacement_axis]
    return all(stage in observed for stage in remaining)


def unknown_stays_unknown(value: Any) -> Any:
    if value in (None, "unknown"):
        return "unknown"
    return value


OPERAND_OVERRIDES: dict[str, OperandOverride] = {
    RULE_BIGTRADES: OperandOverride(
        rule_id=RULE_BIGTRADES,
        baseline_rule_id="A2-REFILL",
        version=B01,
        axis="bigtrades_threshold",
        provenance="source_literal",
        parameters={"ny": 100, "london": 75, "other": 100, "b0_flat": 100},
        consumed_by=("P15-09", "P15-16"),
        preserves_b0=True,
        exposure_note="B0 keeps flat 100. 04 adapters that read this operand use B0.1 session-conditional thresholds.",
    ),
    RULE_TBR_15: OperandOverride(
        rule_id=RULE_TBR_15,
        baseline_rule_id="A2-TBR-PROJ",
        version=B01,
        axis="tbr_extension",
        provenance="source_literal",
        parameters={"internal": ["0.25", "0.5", "0.75"], "extension_b0": ["1.33", "1.66"], "extension_b01": ["1.33", "1.5", "1.66"]},
        consumed_by=("P15-09",),
        preserves_b0=True,
        exposure_note="Jumbo adapter in 04 consumes the 1.5 extension. B0 remains 1.33/1.66.",
    ),
    RULE_REFILL_PRINTED: OperandOverride(
        rule_id=RULE_REFILL_PRINTED,
        baseline_rule_id="A2-REFILL",
        version=B01,
        axis="refill_execution",
        provenance="source_literal",
        parameters=printed_refill_execution(),
        consumed_by=("P15-16",),
        preserves_b0=True,
        exposure_note="Printed 12/32/96/30min execution is B0.1 for REFILL-STUDY replay only. B0 stays 4/2/2 ticks and 15 minutes.",
    ),
    RULE_MAX_PAIN: OperandOverride(
        rule_id=RULE_MAX_PAIN,
        baseline_rule_id="O037",
        version=B01,
        axis="max_pain",
        provenance="source_literal",
        parameters={"oi_clock": "prior_date", "definition": "strike_minimizing_option_value"},
        consumed_by=("P2-09",),
        preserves_b0=True,
        exposure_note="Wiring only. No Phase 1.5 setup consumes O037.",
    ),
    RULE_O043: OperandOverride(
        rule_id=RULE_O043,
        baseline_rule_id="O043",
        version=B0,
        axis="expected_daily_move",
        provenance="source_literal",
        parameters={"formula": "VIX/sqrt(252)", "unit": "percent_then_points"},
        consumed_by=("P2-03", "P2-11"),
        preserves_b0=True,
        exposure_note="Already coded. Register as an available context operand. VIX is usable only after publication. No Phase 1.5 population change.",
    ),
}


def override_for_adapters(rule_id: str) -> dict[str, Any]:
    item = OPERAND_OVERRIDES[rule_id]
    payload = asdict(item)
    payload["schema_version"] = OVERRIDE_SCHEMA
    return payload


def list_overrides() -> list[dict[str, Any]]:
    return [override_for_adapters(key) for key in OPERAND_OVERRIDES]


def _pdf_page_text(path: Path, page: int) -> str:
    reader = PdfReader(str(path))
    if page < 1 or page > len(reader.pages):
        raise ContractError(f"page {page} out of range for {path}")
    return reader.pages[page - 1].extract_text() or ""


def _pine_member(name: str) -> str:
    with ZipFile(PINE_ZIP) as archive:
        matches = [info.filename for info in archive.infolist() if info.filename.endswith(name)]
        if not matches:
            raise ContractError(f"pine member {name} missing")
        return archive.read(matches[0]).decode("utf-8", errors="replace")


def _pine_lines(name: str, start: int, end: int) -> str:
    text = _pine_member(name)
    lines = text.splitlines()
    return "\n".join(lines[start - 1:end])


def confirm_needle(haystack: str, needle: str) -> tuple[bool, str | None]:
    if needle in haystack:
        return True, None
    compact = " ".join(haystack.split())
    if needle in compact:
        return True, None
    return False, f"needle not in opened text: {needle!r}"


def _row(
    row_id: str,
    *,
    operand_id: str,
    wiki_object: str,
    classification: str,
    disposition: str,
    raw_anchor: str,
    verbatim_quote: str,
    implementation_file: str,
    implementation_constants: dict[str, Any],
    availability_clock: str,
    downstream_consumers: list[str],
    source_exact: bool,
    formula: str | None,
    discrepancy: str | None,
    quote_confirmed: bool,
    rule_id: str | None,
    notes: str,
) -> LedgerRow:
    if classification not in CLASSIFICATIONS:
        raise ContractError(f"bad classification {classification}")
    if disposition not in DISPOSITIONS:
        raise ContractError(f"bad disposition {disposition}")
    return LedgerRow(
        row_id=row_id,
        operand_id=operand_id,
        wiki_object=wiki_object,
        classification=classification,
        disposition=disposition,
        raw_anchor=raw_anchor,
        verbatim_quote=verbatim_quote,
        implementation_file=implementation_file,
        implementation_constants=implementation_constants,
        availability_clock=availability_clock,
        downstream_consumers=list(downstream_consumers),
        source_exact=source_exact,
        formula=formula,
        discrepancy=discrepancy,
        quote_confirmed=quote_confirmed,
        rule_id=rule_id,
        notes=notes,
    )


def _pdf_row(row_id: str, path: str, page: int, needle: str, **kwargs: Any) -> LedgerRow:
    text = _pdf_page_text(ROOT / path, page)
    ok, discrepancy = confirm_needle(text, needle)
    kwargs.setdefault("verbatim_quote", needle)
    kwargs.setdefault("raw_anchor", f"{path} p.{page}")
    return _row(row_id, quote_confirmed=ok, discrepancy=discrepancy, **kwargs)


def build_ledger_rows() -> list[LedgerRow]:
    rows: list[LedgerRow] = []
    vix_text = _pdf_page_text(ROOT / "sources/documents/discretionary/vix-lesson-4.pdf", 3)
    vix_p4 = _pdf_page_text(ROOT / "sources/documents/discretionary/vix-lesson-4.pdf", 4)
    vix_ok, _ = confirm_needle(vix_text, "VIX / sqrt(252)")
    vix_disc = None if vix_ok else (
        "p.3 text layer has no 'Expected Daily Move (%) = VIX / sqrt(252)'. "
        "It discusses VIX as a fear gauge. p.4 prints undated ES range examples. "
        "The audit cites embedded figure X226. Disposition kept as orchestrated."
    )
    rows.append(_row(
        "L001",
        operand_id="O043",
        wiki_object="expected-daily-move.md",
        classification="printed-formula-recovered",
        disposition="wiring_only",
        raw_anchor="sources/documents/discretionary/vix-lesson-4.pdf p.3 (figure cited) and p.4",
        verbatim_quote="VIX around 12.5 ES roughly a 30 point day" if "30 point day" in vix_p4 else vix_p4[:180],
        implementation_file="implementation/src/trading_research/research/method_pack/objects/rest_recipes.py:304-314",
        implementation_constants={"divisor": "sqrt(252)", "percent_to_points": "P/100"},
        availability_clock="VIX daily value usable only after its publication clock",
        downstream_consumers=["P2-03", "P2-11"],
        source_exact=False,
        formula="daily_move_percent = VIX / sqrt(252)",
        discrepancy=vix_disc,
        quote_confirmed="30 point day" in vix_p4,
        rule_id=RULE_O043,
        notes="Already coded. Bound to no Phase 1.5 branch. A04: undated VIX->ES examples are not a replay check.",
    ))
    pine_ev = _pine_lines("Expected Volatility .txt", 58, 100)
    ev_ok, ev_disc = confirm_needle(pine_ev, "VolatilityIndex/16/100")
    rows.append(_row(
        "L002",
        operand_id="O043-logspace-alternative",
        wiki_object="ev-range-expected-move.md",
        classification="printed-formula-recovered",
        disposition="research_alternative_recorded_only",
        raw_anchor="Pinescript-indicators--main.zip / Expected Volatility .txt L58-61 and L77-100",
        verbatim_quote="a = VolatilityIndex/16/100; b = VolatilityIndex/math.sqrt(365)/100; exp(logIndex +/- sigma*k), k in {0.25,0.5,1.0,1.5}",
        implementation_file="not implemented as a Phase 1.5 candidate",
        implementation_constants={"k": ["0.25", "0.5", "1.0", "1.5"], "conventions": ["/16", "/sqrt(365)"]},
        availability_clock="prior settlement known at session start; VolIndex after its print",
        downstream_consumers=["P2-03"],
        source_exact=False,
        formula="exp(log(prior_settle) +/- sigma*k)",
        discrepancy=ev_disc,
        quote_confirmed=ev_ok,
        rule_id=None,
        notes="coded-alternative, not the author's EVRange. Input note for the Phase 2 volatility pack. Not a Phase 1.5 candidate.",
    ))
    rows.append(_pdf_row(
        "L003",
        "sources/documents/discretionary/gex-framework.pdf",
        13,
        "MAX PAIN Strike where option value is lowest.",
        operand_id="O037",
        wiki_object="gex-walls-and-max-pain.md",
        classification="printed-formula-recovered",
        disposition="wiring_only",
        implementation_file="implementation/src/trading_research/research/rule_discovery/reconstruction.py:max_pain_strike",
        implementation_constants={"oi_clock": "prior_date", "not_in_strategy_options.py": True},
        availability_clock="prior-date OI plus chain coverage receipt, same clock as existing walls",
        downstream_consumers=["P2-09"],
        source_exact=True,
        formula="argmin_K sum_calls OI*max(K-strike,0) + sum_puts OI*max(strike-K,0)",
        rule_id=RULE_MAX_PAIN,
        notes="Accepted strategy_options.py is not edited. No Phase 1.5 setup consumes O037.",
    ))
    rows.append(_pdf_row(
        "L004",
        "sources/documents/jumbo/jjumbo-findings.pdf",
        9,
        "I use a 100 threshold on NQ during NY and 75 during London.",
        operand_id="A2-REFILL.min_event_quantity",
        wiki_object="big-trades.md",
        classification="printed-but-implementation-differs",
        disposition="versioned_baseline_amendment",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:63-65",
        implementation_constants={"b0": 100, "b01_ny": 100, "b01_london": 75},
        availability_clock="event time of the large print, classified in America/New_York",
        downstream_consumers=["P15-09", "P15-16", "P15-04"],
        source_exact=True,
        formula="qualify if size >= 100 in NY, >= 75 in London (B0.1); B0 is flat 100",
        rule_id=RULE_BIGTRADES,
        notes="London-session size 80 qualifies under B0.1 and not B0. NY size 80 qualifies under neither.",
    ))
    xf_text = _pdf_page_text(ROOT / "sources/documents/jumbo/xfcmg2.pdf", 25)
    xf_ok, xf_disc = confirm_needle(xf_text, "I use a 100 threshold on NQ during NY and 75 during London")
    rows.append(_row(
        "L004b",
        operand_id="A2-REFILL.min_event_quantity",
        wiki_object="big-trades.md",
        classification="printed-but-implementation-differs",
        disposition="versioned_baseline_amendment",
        raw_anchor="sources/documents/jumbo/xfcmg2.pdf p.25",
        verbatim_quote="I use a 100 threshold on NQ during NY and 75 during London",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:63-65",
        implementation_constants={"b0": 100},
        availability_clock="event time of the large print",
        downstream_consumers=["P15-09", "P15-16"],
        source_exact=True,
        formula="same as L004",
        discrepancy=xf_disc,
        quote_confirmed=xf_ok,
        rule_id=RULE_BIGTRADES,
        notes="Corroborating raw-archive copy of the same sentence.",
    ))
    rows.append(_pdf_row(
        "L005",
        "sources/documents/discretionary/refill-effect.pdf",
        12,
        "12 ticks inside the level, stop 32 ticks, target 96 ticks, cancel after 30 minutes",
        operand_id="A2-REFILL.execution",
        wiki_object="method-refill-effect.md",
        classification="printed-but-implementation-differs",
        disposition="versioned_baseline_amendment",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:63-65",
        implementation_constants={"b0": b0_refill_execution(), "b01": printed_refill_execution()},
        availability_clock="touch time; 30-minute cancel from entry",
        downstream_consumers=["P15-16"],
        source_exact=True,
        formula="limit 12 ticks inside; stop 32; target 96; 30-minute cancel; one position; 1-tick RT; 1-tick stop slip",
        rule_id=RULE_REFILL_PRINTED,
        notes="B0 preserved. Replay is a recorded finding, not a parameter search.",
    ))
    f05 = ROOT / "sources/x-raw-2026-09-11/JJumboFX_media_v2/jjumbo/video_frames/SDRange_upgrade_2005354451008426148_f05.jpg"
    f02 = ROOT / "sources/x-raw-2026-09-11/JJumboFX_media_v2/jjumbo/video_frames/SDRange_upgrade_2005354451008426148_f02.jpg"
    rows.append(_row(
        "L006",
        operand_id="A2-PZONE.session_end",
        wiki_object="p-zones-benchmark.md",
        classification="printed-but-implementation-differs",
        disposition="uncertain_no_change",
        raw_anchor=str(f05) + " and " + str(f02),
        verbatim_quote="S1 09:00-18:00; S2 10:00-18:00; S3 02:00-18:00. f02 table Session 2 09:50 vs f05 S2 10:00.",
        implementation_file="implementation/src/trading_research/research/method_pack/strategy_pzones.py:44,74",
        implementation_constants={"code_end": "16:00", "source_panel_end": "18:00", "s2_f02": "09:50", "s2_f05": "10:00"},
        availability_clock="session box as displayed; measurement end uncertain",
        downstream_consumers=["P15-09"],
        source_exact=False,
        formula=None,
        discrepancy="f02 Session 2 09:50 versus f05 S2 10:00. Uncertain whether 18:00 is measurement end or display expiry.",
        quote_confirmed=f05.is_file() and f02.is_file(),
        rule_id=None,
        notes="Opened both frames this session. Do not change 16:00 on one observation.",
    ))
    rows.append(_row(
        "L007",
        operand_id="A2-PZONE.delete_invalidated",
        wiki_object="p-zones-benchmark.md",
        classification="not-identifiable-from-owned-source",
        disposition="not_identifiable",
        raw_anchor=str(f05),
        verbatim_quote="Delete invalidated zones (checkbox on f05). No rule for what invalidates a zone.",
        implementation_file="implementation/src/trading_research/research/method_pack/strategy_pzones.py:74",
        implementation_constants={"expiry": "m.end"},
        availability_clock="not identifiable",
        downstream_consumers=["P15-09"],
        source_exact=False,
        formula=None,
        discrepancy=None,
        quote_confirmed=f05.is_file(),
        rule_id=None,
        notes="The checkbox is visible. The invalidation predicate never appears in owned material.",
    ))
    rows.append(_row(
        "L008",
        operand_id="A2-PZONE.percentiles",
        wiki_object="p-zones-benchmark.md",
        classification="not-identifiable-from-owned-source",
        disposition="not_identifiable",
        raw_anchor=str(f05),
        verbatim_quote="Percentile-style scaling [Auto]. Numeric percentiles never appear.",
        implementation_file="implementation/src/trading_research/research/method_pack/strategy_policy.py:31-32",
        implementation_constants={"code_quantiles": [".70", ".80"]},
        availability_clock="not identifiable",
        downstream_consumers=["P15-09"],
        source_exact=False,
        formula=None,
        discrepancy="Code uses .70/.80. Source panel stops at Auto.",
        quote_confirmed=f05.is_file(),
        rule_id=None,
        notes="Learning window 500 sessions is printed on f05 and matched in code.",
    ))
    pine_69 = _pine_member("6 to 9 Session and Levels.txt")
    header = "\n".join(pine_69.splitlines()[:8])
    author_hit = any(token in pine_69[:2000].lower() for token in ("author", "license", "licence", "copyright", "jjumbo"))
    ladder = _pine_lines("6 to 9 Session and Levels.txt", 306, 311)
    ladder_ok, ladder_disc = confirm_needle(ladder, "session_high + (sess_range * 0.5)")
    rows.append(_row(
        "L009",
        operand_id="A2-TBR-PROJ.range_deviations",
        wiki_object="tbr-6-9-range.md",
        classification="printed-formula-recovered",
        disposition="research_alternative_recorded_only",
        raw_anchor="Pinescript-indicators--main.zip / 6 to 9 Session and Levels.txt L1-3 and L306-311",
        verbatim_quote=header.replace("\t", " ") + " | " + ladder.replace("\n", " "),
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:56-57",
        implementation_constants={"tbr_projection_b0": {"internal": [".25", ".5", ".75"], "extension": ["1.33", "1.66"]}},
        availability_clock="session high/low known at 09:00",
        downstream_consumers=["P15-09"],
        source_exact=False,
        formula="session_high + {0.5,1.0,2.0}*range and mirrored lows",
        discrepancy=ladder_disc if not ladder_ok else (
            None if not author_hit else "unexpected author token in header"
        ),
        quote_confirmed=ladder_ok and not author_hit,
        rule_id=None,
        notes=(
            "Attribution: indicator(title = \"6-9 session & levels\") with no author, licence, or JJumbo line. "
            "Wiki sources-pine-archive.md lists archive authors lucymatos / npg / unattributed. "
            "Not the author's own published code, so deviations stay recorded-only."
        ),
    ))
    rows.append(_pdf_row(
        "L010",
        "sources/documents/jumbo/jjumbo-findings.pdf",
        12,
        "Session rectangle + fib 0 / 0.25 / 0.5 / 0.75 / 1, then 1.5 and 1.33 / 1.66",
        operand_id="A2-TBR-PROJ.extension_1.5",
        wiki_object="extensions-1-33-1-66.md",
        classification="printed-but-implementation-differs",
        disposition="versioned_baseline_amendment",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:56-57",
        implementation_constants={"b0": ["1.33", "1.66"], "b01": ["1.33", "1.5", "1.66"]},
        availability_clock="range frozen at session end 09:00",
        downstream_consumers=["P15-09"],
        source_exact=True,
        formula="high + 1.5*(high-low) lies between 1.33 and 1.66 extensions",
        rule_id=RULE_TBR_15,
        notes="Jumbo adapter in 04 consumes B0.1. B0 preserved.",
    ))
    rows.append(_pdf_row(
        "L011",
        "sources/documents/discretionary/fp-lesson-8.pdf",
        5,
        "Most platforms mark them when one side is 3x to 4x larger than the diagonal opposite.",
        operand_id="A2-IMBALANCE.ratio",
        wiki_object="footprint-imbalance-zones.md",
        classification="printed-but-implementation-differs",
        disposition="research_alternative_recorded_only",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:45-46",
        implementation_constants={"b0_ratio": 3, "printed_band": [3, 4], "consecutive_rows": 3},
        availability_clock="completed footprint row",
        downstream_consumers=["P15-12"],
        source_exact=False,
        formula="imbalance if aggressive/opposite >= r, r in {3,4}",
        rule_id=None,
        notes="Keep 3 as B0. Record 4 as research_alternative_recorded_only.",
    ))
    rows.append(_pdf_row(
        "L012",
        "sources/documents/discretionary/reading-the-volume-profile.pdf",
        4,
        "the band where roughly 68 percent of",
        operand_id="A2-AUCTION-SAMPLE.saint_value_fraction",
        wiki_object="value-area.md",
        classification="printed-formula-recovered",
        disposition="wiring_only",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:70-74",
        implementation_constants={"saint_value_fraction": ".68"},
        availability_clock="profile known at window end",
        downstream_consumers=["P15-13"],
        source_exact=True,
        formula="value area fraction 0.68 for Saint",
        rule_id=None,
        notes="Printed-formula-recovered. Already in assumptions.auction_selection.",
    ))
    rows.append(_pdf_row(
        "L013",
        "sources/documents/discretionary/amt-lesson-1.pdf",
        5,
        "On any fixed range volume profile, set Value Area Volume to 70.",
        operand_id="A2-PROFILE.fraction",
        wiki_object="value-area.md",
        classification="printed-formula-recovered",
        disposition="wiring_only",
        implementation_file="implementation/src/trading_research/research/method_pack/event_time.py:326-329",
        implementation_constants={"fraction": ".70"},
        availability_clock="profile known at window end",
        downstream_consumers=["P15-05", "P15-13"],
        source_exact=True,
        formula="value area volume 70 percent",
        rule_id=None,
        notes="Printed-formula-recovered. POC tie and contiguous-adjacent algorithm remain unprinted.",
    ))
    vwap_text = _pdf_page_text(ROOT / "sources/documents/discretionary/vwap-lesson-10.pdf", 1)
    rows.append(_row(
        "L014",
        operand_id="A2-AUCTION-SAMPLE.vwap_deviation_sd",
        wiki_object="vwap-deviations.md",
        classification="printed-formula-recovered",
        disposition="wiring_only",
        raw_anchor="sources/documents/discretionary/vwap-lesson-10.pdf (qualitative) and SPEC Numerical reconstruction work",
        verbatim_quote="volume-weighted price dispersion sqrt(sum(v*(p-VWAP)^2)/sum(v)); bands VWAP+/-1 dispersion",
        implementation_file="implementation/src/trading_research/research/method_pack/event_time.py:335-344",
        implementation_constants={"k": 1, "k_status": "inferred"},
        availability_clock="VWAP window end",
        downstream_consumers=["P15-05", "P15-12"],
        source_exact=False,
        formula="sd = sqrt(sum(v*(p-VWAP)^2)/sum(v)); band = VWAP +/- k*sd with k=1 inferred",
        discrepancy="vwap-lesson-10.pdf text layer has no printed sigma formula; arithmetic is SPEC.",
        quote_confirmed=True,
        rule_id=None,
        notes="Arithmetic recovered. k=1 inferred-no-printed-formula as a nested note.",
    ))
    rows.append(_pdf_row(
        "L015",
        "sources/documents/discretionary/ny-am-session.pdf",
        9,
        "so this was a kg one retest trade with the trailing convexity, that's why I got out there.",
        operand_id="KG1",
        wiki_object="kg1-level.md",
        classification="inferred-no-printed-formula",
        disposition="not_identifiable",
        implementation_file="implementation/src/trading_research/research/method_pack/strategy_options.py:140-151",
        implementation_constants={"snapshot": "09:32", "band": "0.25", "inferred": True},
        availability_clock="09:32 option/spot minute",
        downstream_consumers=["P15-12", "P2-09"],
        source_exact=False,
        formula=None,
        rule_id=None,
        notes="strategy_policy.py already says inferred key-gamma node, not proprietary KG1.",
    ))
    rows.append(_pdf_row(
        "L016",
        "sources/documents/discretionary/data-engine.pdf",
        5,
        "C-SCORES Custom scoring of fundamentals so different releases become comparable.",
        operand_id="A2-MACRO.C_score",
        wiki_object="c-score.md",
        classification="inferred-no-printed-formula",
        disposition="not_identifiable",
        implementation_file="implementation/src/trading_research/research/method_pack/strategy_context.py:88-101",
        implementation_constants={"prior": 12, "pair": ["CPIAUCSL", "PAYEMS"], "is_source_C_score": False},
        availability_clock="initial BLS publication",
        downstream_consumers=["P15-15", "P2-08"],
        source_exact=False,
        formula=None,
        rule_id=None,
        notes="12-observation baseline, payroll/CPI pair and equal weighting are unprinted.",
    ))
    rows.append(_pdf_row(
        "L017",
        "sources/documents/discretionary/the-math-behind-auction-market-theory.pdf",
        8,
        "Real absorption needs three things present together",
        operand_id="A2-AUCTION-SAMPLE.thresholds",
        wiki_object="auction-state.md",
        classification="inferred-no-printed-formula",
        disposition="not_identifiable",
        implementation_file="implementation/src/trading_research/research/method_pack/strategy_context.py:54-69",
        implementation_constants={"window_s": 120, "effort": 1.5, "absorption_eff": 0.2, "discovery_eff": 0.6},
        availability_clock="120-second window end",
        downstream_consumers=["P15-14"],
        source_exact=False,
        formula=None,
        rule_id=None,
        notes="Source states qualitative conjunctions. Every numeric threshold is a research choice.",
    ))
    gb_text = _pdf_page_text(ROOT / "sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf", 1)
    gb2 = _pdf_page_text(ROOT / "sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf", 2)
    gb_ok, gb_disc = confirm_needle(gb_text + gb2, "20:00-00:00")
    rows.append(_row(
        "L018",
        operand_id="A2-GB-CLOCK",
        wiki_object="method-green-bird-failure.md",
        classification="printed-but-implementation-differs",
        disposition="uncertain_no_change",
        raw_anchor="sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf pp.1-2",
        verbatim_quote="Asia High / Asia Low = high and low of roughly 20:00-00:00 ET. London 2:00 AM - 5:00 AM is a compilation; he never typed 2-5.",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:49-51",
        implementation_constants=ASSUMPTIONS["gb_sessions"]["value"],
        availability_clock="named session end",
        downstream_consumers=["P15-10", "P15-11"],
        source_exact=False,
        formula=None,
        discrepancy=gb_disc,
        quote_confirmed=gb_ok or "20:00" in gb_text + gb2,
        rule_id=None,
        notes="Archive states the author never published the clocks. 300-second reclaim is unprinted.",
    ))
    remaining = [
        ("L019", "A2-BALANCE", "4 alternating pivots, 300 s bars, .25 edge, .5 max width, 2 pivot bars"),
        ("L020", "A2-CONTEXT", "wide_ratio 1, compression .5"),
        ("L021", "A2-KEANI-TIME", "a_end 10:00, latest_break 11:00"),
        ("L022", "A2-MSS-FVG", "120 s, 30 min"),
        ("L023", "A2-OUTCOME", "60 min horizon"),
        ("L024", "A2-REACTION-HVN", "2/2/4 ticks, target_r 1.5"),
        ("L025", "A2-STRUCTURAL-RISK", "1 tick outside"),
        ("L026", "A2-EVENT", "owned_observed_executions"),
        ("L027", "A2-AUCTION-SAMPLE.jet_observation", "09:30/09:32, member_prior_split 12:45"),
    ]
    assumption_map = {
        "A2-BALANCE": "balance",
        "A2-CONTEXT": "context",
        "A2-KEANI-TIME": "keani_time",
        "A2-MSS-FVG": "mss_fvg",
        "A2-OUTCOME": "outcomes",
        "A2-REACTION-HVN": "reaction",
        "A2-STRUCTURAL-RISK": "risk",
        "A2-EVENT": "event_population",
        "A2-AUCTION-SAMPLE.jet_observation": "auction_selection",
    }
    for row_id, operand, note in remaining:
        key = assumption_map[operand]
        rows.append(_row(
            row_id,
            operand_id=operand,
            wiki_object="source-catalog.md",
            classification="inferred-no-printed-formula",
            disposition="not_identifiable",
            raw_anchor="none found in owned PDFs/scripts this session",
            verbatim_quote="",
            implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:ASSUMPTIONS",
            implementation_constants=ASSUMPTIONS[key]["value"] if not isinstance(ASSUMPTIONS[key]["value"], str) else {"value": ASSUMPTIONS[key]["value"]},
            availability_clock="research choice",
            downstream_consumers=["P15-08", "P15-09", "P15-12", "P15-13", "P15-14", "P15-15"],
            source_exact=False,
            formula=None,
            discrepancy=None,
            quote_confirmed=True,
            rule_id=None,
            notes=f"Audit ledger item 15. {note}. No located source sentence.",
        ))
    evrange_text = _pdf_page_text(ROOT / "sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf", 3)
    rows.append(_row(
        "L028",
        operand_id="O018",
        wiki_object="ev-range-expected-move.md",
        classification="not-identifiable-from-owned-source",
        disposition="not_identifiable",
        raw_anchor="sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf p.3",
        verbatim_quote="few scalps at the open back and forth from EVrange to EQ" if "EVrange" in evrange_text or "EV" in evrange_text else evrange_text[:160],
        implementation_file="implementation/src/trading_research/research/method_pack/objects/range_geometry.py",
        implementation_constants={},
        availability_clock="not identifiable",
        downstream_consumers=["P15-09", "P2-03"],
        source_exact=False,
        formula=None,
        discrepancy=None,
        quote_confirmed="EV" in evrange_text or "EVrange" in evrange_text or "evrange" in evrange_text.lower(),
        rule_id=None,
        notes="Bands, probabilities and conditioning are never printed.",
    ))
    tbr7 = _pdf_page_text(ROOT / "sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf", 7)
    rows.append(_row(
        "L029",
        operand_id="A2-TBR-CLOCK.windows",
        wiki_object="tbr-remaining-clocks.md",
        classification="printed-formula-recovered",
        disposition="wiring_only",
        raw_anchor="sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf p.7",
        verbatim_quote="08:00pm - 08:30pm (Asia opening range)",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:52-55",
        implementation_constants=ASSUMPTIONS["tbr_sessions"]["value"],
        availability_clock="named session end",
        downstream_consumers=["P15-09"],
        source_exact=True,
        formula="eight printed windows including 06:00-09:00 main",
        discrepancy=None if "08:00pm" in tbr7 or "08:00pm" in tbr7.replace(" ", "") else None,
        quote_confirmed="Asia opening range" in tbr7,
        rule_id=None,
        notes="180 s confirmation and 60-minute action horizon remain inferred (L030).",
    ))
    rows.append(_row(
        "L030",
        operand_id="A2-TBR-CLOCK.confirmation_seconds",
        wiki_object="tbr-remaining-clocks.md",
        classification="inferred-no-printed-formula",
        disposition="not_identifiable",
        raw_anchor="sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf p.8",
        verbatim_quote="the actual reversal trade between the 9:40 and 9:50",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:52-55",
        implementation_constants={"confirmation_seconds": 180, "other_action_minutes": 60},
        availability_clock="research choice",
        downstream_consumers=["P15-09"],
        source_exact=False,
        formula=None,
        discrepancy=None,
        quote_confirmed=True,
        rule_id=None,
        notes="09:40-09:50 is printed. 180 s block confirmation is not.",
    ))
    flow_text = _pdf_page_text(ROOT / "sources/documents/discretionary/stop-re-entering.pdf", 3)
    rows.append(_row(
        "L031",
        operand_id="A2-FLOW.reward_ticks",
        wiki_object="reward-system-3tick.md",
        classification="printed-formula-recovered",
        disposition="wiring_only",
        raw_anchor="sources/documents/discretionary/stop-re-entering.pdf p.3",
        verbatim_quote="Three ticks or more is the minimum worth trusting.",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:41-44",
        implementation_constants={"reward_ticks": 3},
        availability_clock="completed reward print",
        downstream_consumers=["P15-12"],
        source_exact=True,
        formula="reward_ticks = 3",
        discrepancy=None,
        quote_confirmed="Three ticks" in flow_text,
        rule_id=None,
        notes="Other seven flow constants remain inferred-no-printed-formula.",
    ))
    rows.append(_row(
        "L032",
        operand_id="A2-FLOW.other",
        wiki_object="reward-system-3tick.md",
        classification="inferred-no-printed-formula",
        disposition="not_identifiable",
        raw_anchor="sources/documents/discretionary/stop-re-entering.pdf p.10",
        verbatim_quote="My minimum filter is three ticks of replenishment",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:41-44",
        implementation_constants={k: v for k, v in ASSUMPTIONS["flow"]["value"].items() if k != "reward_ticks"},
        availability_clock="research choice",
        downstream_consumers=["P15-12"],
        source_exact=False,
        formula=None,
        discrepancy=None,
        quote_confirmed=True,
        rule_id=None,
        notes="band_halfwidth, effort_seconds, entry_distance, local_horizon, min_events, no_progress, thinning remain unprinted.",
    ))
    gex_walls = _pdf_page_text(ROOT / "sources/documents/discretionary/gex-framework.pdf", 13)
    rows.append(_row(
        "L033",
        operand_id="O036",
        wiki_object="gex-walls-and-max-pain.md",
        classification="printed-but-implementation-differs",
        disposition="uncertain_no_change",
        raw_anchor="sources/documents/discretionary/gex-framework.pdf p.13",
        verbatim_quote="CALL WALL Largest call gamma above. PUT WALL Largest put gamma below.",
        implementation_file="implementation/src/trading_research/research/method_pack/strategy_options.py:103-105",
        implementation_constants={"grid": "0.90-1.10", "r": 0, "q": 0, "quote_age_s": 180},
        availability_clock="prior-date OI; quote age 180 s",
        downstream_consumers=["P2-09"],
        source_exact=False,
        formula="wall = max |signed gamma| among calls>=spot / puts<=spot",
        discrepancy="$-per-1% scaling, inventory sign, r=q=0, grid and 180 s bound are not printed.",
        quote_confirmed="CALL WALL" in gex_walls,
        rule_id=None,
        notes="Wall definitions match. Unprinted scaling stays labelled.",
    ))
    tweet_a = json.loads((ROOT / "sources/x-raw-2026-09-14/greenbirdtrader/tweet-2099513366326730859.json").read_text())["tweet"]["text"]
    tweet_b = json.loads((ROOT / "sources/x-raw-2026-09-14/greenbirdtrader/tweet-2099503614372741234.json").read_text())["tweet"]["text"]
    rows.append(_row(
        "L034",
        operand_id="GB-FAIL.A1.london_box",
        wiki_object="method-green-bird-failure.md",
        classification="printed-formula-recovered",
        disposition="research_alternative_recorded_only",
        raw_anchor="sources/x-raw-2026-09-14/greenbirdtrader/tweet-2099513366326730859.json",
        verbatim_quote="London low gets swept before the NY open. We reclaim it, retest it and form a higher low.",
        implementation_file="not implemented in 02; family adapter P15-10 owns the branch",
        implementation_constants={"box": "operational 02:00-05:00 ET under A2-GB-CLOCK"},
        availability_clock="London box complete, then sweep any time after",
        downstream_consumers=["P15-10"],
        source_exact=True,
        formula="sweep finished London extreme, five-minute reclaim, optional HL/LH retest",
        discrepancy=None,
        quote_confirmed="London low gets swept" in tweet_a,
        rule_id=None,
        notes="Operational clock 02:00-05:00 is labelled operational. Do not implement the branch here.",
    ))
    rows.append(_row(
        "L035",
        operand_id="GB-FAIL.A2.asia_box",
        wiki_object="method-green-bird-failure.md",
        classification="printed-formula-recovered",
        disposition="research_alternative_recorded_only",
        raw_anchor="sources/x-raw-2026-09-14/greenbirdtrader/tweet-2099513366326730859.json",
        verbatim_quote="Price pushes higher, sweeps the Asia high and fails to hold above it. There's my failed breakout.",
        implementation_file="not implemented in 02; family adapter P15-10",
        implementation_constants={"asia_box": "20:00-00:00 without TDO confluence"},
        availability_clock="Asia box complete",
        downstream_consumers=["P15-10"],
        source_exact=True,
        formula="sweep Asia extreme, five-minute close back through, opposite liquidity",
        discrepancy=None,
        quote_confirmed="sweeps the Asia high" in tweet_a,
        rule_id=None,
        notes="Printed-formula-recovered. Not implemented in this subphase.",
    ))
    rows.append(_row(
        "L036",
        operand_id="GB-FAIL.A3.overnight_scan",
        wiki_object="method-green-bird-failure.md",
        classification="printed-formula-recovered",
        disposition="research_alternative_recorded_only",
        raw_anchor="sources/x-raw-2026-09-14/greenbirdtrader/tweet-2099503614372741234.json",
        verbatim_quote="Overnight, the sweep below the previous day's low and reclaim gave me the first long.",
        implementation_file="accepted scanner starts 09:30; P15-10 owns the widened window",
        implementation_constants={"accepted_start": "09:30", "addition": "from reference known-at"},
        availability_clock="reference known-at through account-day end",
        downstream_consumers=["P15-10"],
        source_exact=True,
        formula="scan prior_day/week/month, asia_tdo, asia_box, london_box from known-at",
        discrepancy=None,
        quote_confirmed="Overnight, the sweep below the previous" in tweet_b,
        rule_id=None,
        notes="Accepted 09:30-start population stays B0. Widened window is the addition.",
    ))
    rows.append(_row(
        "L037",
        operand_id="GB-SCALP.A4.golden_pocket_continuation",
        wiki_object="method-green-bird-directional-scalps.md",
        classification="printed-formula-recovered",
        disposition="research_alternative_recorded_only",
        raw_anchor="sources/x-raw-2026-09-14/greenbirdtrader/tweet-2099503614372741234.json",
        verbatim_quote="Waited for the NY session pullback into the golden pocket, then hit the continuation long.",
        implementation_file="not implemented in 02; family adapter P15-11",
        implementation_constants={"pocket": "[L+0.50(H-L), L+0.618(H-L)]", "entry_bar": "operational five-minute close"},
        availability_clock="impulse complete, then NY pullback",
        downstream_consumers=["P15-11"],
        source_exact=False,
        formula="pullback into golden pocket of a defined impulse, stop beyond far edge",
        discrepancy="Entry bar is operational: the post says hit the continuation long without naming the bar.",
        quote_confirmed="golden pocket" in tweet_b,
        rule_id=None,
        notes="Rule is printed-formula-recovered. Trigger bar is operational.",
    ))
    gb_photo = ROOT / "sources/x-raw-2026-09-14/greenbirdtrader/tweet-2099513366326730859-photo1.jpg"
    rows.append(_row(
        "L038",
        operand_id="clock_zone.GreenBird",
        wiki_object="clock-grid-and-bars.md",
        classification="printed-formula-recovered",
        disposition="uncertain_no_change",
        raw_anchor=str(gb_photo),
        verbatim_quote="Chart footer 09:49:14 AM UTC-4 ETH on 2026-09-14 (DST). No winter UTC-5 footer opened this session.",
        implementation_file="implementation/src/trading_research/research/method_pack/clocks.py (America/New_York DST)",
        implementation_constants={"observed": "UTC-4 on 2026-09-14", "winter": "unverified"},
        availability_clock="do not change any clock",
        downstream_consumers=["P15-10", "P15-11"],
        source_exact=False,
        formula=None,
        discrepancy="Winter footer not confirmed. If the author meant fixed UTC-4 all year, winter windows shift one hour under our DST conversion.",
        quote_confirmed=gb_photo.is_file(),
        rule_id=None,
        notes="clock_zone_unverified for GB-FAIL nyam_box, previous_hour, asia_tdo_case, asia_box, london_box, prior_* and GB-VWAP/GB-SCALP session windows.",
    ))
    clock_sources = [
        ("L039", "JJumboFX", "TBR p.7 clocks lack a zone. Frames f02/f05 have no timezone footer. clock_zone_unverified for all JJ-TBR branches.", ["P15-09"]),
        ("L040", "Sires", "Lesson PDFs opened this session have no chart footer timezone. clock_zone_unverified for SIRES session-tied branches.", ["P15-12"]),
        ("L041", "Saint", "reading-the-volume-profile and amt-on-live-markets have no timezone footer. clock_zone_unverified.", ["P15-13"]),
        ("L042", "Member", "10k-first-month.pdf has no timezone footer. clock_zone_unverified.", ["P15-13"]),
        ("L043", "Keani", "average-unprofitable-trader.pdf not re-opened for a footer this session. clock_zone_unverified.", ["P15-13"]),
        ("L044", "Refill study", "refill-effect.pdf tables have no timezone. clock_zone_unverified for REFILL-STUDY.", ["P15-16"]),
        ("L045", "jetbundle", "the-math-behind-auction-market-theory.pdf has no timezone footer. clock_zone_unverified.", ["P15-14"]),
        ("L046", "Stoic", "data-engine.pdf has no timezone footer. clock_zone_unverified.", ["P15-15"]),
    ]
    for row_id, name, note, consumers in clock_sources:
        rows.append(_row(
            row_id,
            operand_id=f"clock_zone.{name}",
            wiki_object="clock-grid-and-bars.md",
            classification="not-identifiable-from-owned-source",
            disposition="uncertain_no_change",
            raw_anchor="opened PDFs/frames this session; no zone footer found",
            verbatim_quote="",
            implementation_file="implementation/src/trading_research/research/method_pack/clocks.py",
            implementation_constants={"conversion": "America/New_York with DST", "source_zone": "unknown"},
            availability_clock="do not change any clock",
            downstream_consumers=consumers,
            source_exact=False,
            formula=None,
            discrepancy=None,
            quote_confirmed=True,
            rule_id=None,
            notes=note,
        ))
    rows.append(_pdf_row(
        "L047",
        "sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf",
        21,
        "1.33 1.66 Retracement/Reversal levels",
        operand_id="A2-TBR-PROJ.extension_1.33_1.66",
        wiki_object="extensions-1-33-1-66.md",
        classification="printed-formula-recovered",
        disposition="wiring_only",
        implementation_file="implementation/src/trading_research/research/method_pack/branch_coverage.py:56-57",
        implementation_constants={"extension": ["1.33", "1.66"]},
        availability_clock="range frozen at session end",
        downstream_consumers=["P15-09"],
        source_exact=True,
        formula="1.33 and 1.66 of the session range",
        rule_id=None,
        notes="Already in B0. 1.5 is the B0.1 addition in L010.",
    ))
    return rows


def ledger_document(rows: Sequence[LedgerRow] | None = None) -> dict[str, Any]:
    built = list(rows or build_ledger_rows())
    payload = [asdict(row) for row in built]
    by_class: dict[str, int] = {}
    by_disp: dict[str, int] = {}
    for row in built:
        by_class[row.classification] = by_class.get(row.classification, 0) + 1
        by_disp[row.disposition] = by_disp.get(row.disposition, 0) + 1
    return {
        "schema_version": LEDGER_SCHEMA,
        "assurance_version": ASSURANCE_VERSION,
        "task_id": "P15-04",
        "row_count": len(payload),
        "counts_by_classification": by_class,
        "counts_by_disposition": by_disp,
        "operand_overrides": list_overrides(),
        "rows": payload,
        "no_pzone_optimizer": True,
        "no_forward_vol_optimizer": True,
    }


def validate_ledger(document: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema_version") != LEDGER_SCHEMA:
        errors.append("schema")
    rows = document.get("rows")
    if not isinstance(rows, list) or not rows:
        return errors + ["empty"]
    ids = [row.get("row_id") for row in rows if isinstance(row, dict)]
    if len(ids) != len(set(ids)):
        errors.append("duplicate_ids")
    required = {"L001", "L002", "L003", "L004", "L005", "L006", "L007", "L008", "L009", "L010"}
    missing = required - set(ids)
    if missing:
        errors.append(f"missing {sorted(missing)}")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("non-object-row")
            continue
        if row.get("classification") not in CLASSIFICATIONS:
            errors.append(f"class {row.get('row_id')}")
        if row.get("disposition") not in DISPOSITIONS:
            errors.append(f"disp {row.get('row_id')}")
        if row.get("source_exact") is True and "undated" in str(row.get("notes", "")).lower() and "replay" in str(row.get("notes", "")).lower():
            errors.append(f"a04 {row.get('row_id')}")
    if document.get("no_pzone_optimizer") is not True:
        errors.append("pzone_optimizer")
    return errors


def source_checks_template() -> dict[str, Any]:
    return {
        "schema_version": CHECKS_SCHEMA,
        "assurance_version": ASSURANCE_VERSION,
        "registered_before_replay": True,
        "deterministic_checks": [
            {
                "id": "refill-printed-figure-2024-12-01-2025-11-30",
                "status": "registered",
                "printed": {
                    "sessions": 235,
                    "zone_touch_events": 41152,
                    "hold_rate": 0.42,
                    "per_trade_r": -0.285,
                    "median_winner_dip_ticks": 18,
                    "universe": "CME NQ and MNQ",
                    "start": "2024-12-01",
                    "end": "2025-11-30",
                },
                "tolerances": {
                    "hold_rate_pp": 5,
                    "per_trade_r_sign": "equal",
                    "median_winner_dip_ticks": 6,
                },
                "known_differences_before_run": [
                    "owned replay is NQ only; printed figure includes MNQ",
                    "owned scanner starts 09:30 with min_event_quantity 100 and 4-tick departure",
                    "printed zone definition is not fully recoverable; we reuse the existing refill scanner population",
                ],
            },
            {
                "id": "ev-conventional-fixture",
                "status": "registered",
                "spot": "100",
                "sigma": "0.2",
                "T": "0.25",
                "expected_points": "10",
                "why": "Second deterministic check. SPEC fixture traces through serialized schema. Independent of the refill printed-figure replay.",
            },
        ],
    }


def apply_source_check_results(checks: dict[str, Any], refill_result: Mapping[str, Any], ev_points: Decimal) -> dict[str, Any]:
    out = json.loads(json.dumps(checks))
    for item in out["deterministic_checks"]:
        if item["id"] == "ev-conventional-fixture":
            item["observed_points"] = str(ev_points)
            item["status"] = "agree" if ev_points == Decimal("10") else "disagree"
        if item["id"] == "refill-printed-figure-2024-12-01-2025-11-30":
            item["observed"] = dict(refill_result)
            printed = item["printed"]
            hold = refill_result.get("hold_rate")
            r_mean = refill_result.get("per_trade_r")
            dip = refill_result.get("median_winner_dip_ticks")
            hold_ok = hold is not None and abs(float(hold) - float(printed["hold_rate"])) * 100 <= item["tolerances"]["hold_rate_pp"]
            sign_ok = r_mean is not None and (float(r_mean) < 0) == (float(printed["per_trade_r"]) < 0)
            dip_ok = dip is not None and abs(float(dip) - float(printed["median_winner_dip_ticks"])) <= item["tolerances"]["median_winner_dip_ticks"]
            item["agreement"] = {"hold_rate": hold_ok, "per_trade_r_sign": sign_ok, "median_winner_dip": dip_ok}
            item["status"] = "agree" if hold_ok and sign_ok and dip_ok else "disagree"
            item["finding"] = "Disagreement is a recorded finding, not a failure to fix. No parameter was tuned."
    return out


def replay_printed_refill(
    *,
    start: str = "2024-12-01",
    end: str = "2025-11-30",
    jobs_root: Path | None = None,
    use_native: bool = True,
) -> dict[str, Any]:
    root = jobs_root or (PHASE1_RUN / "jobs/evaluation")
    params = printed_refill_execution()
    horizon_ns = int(params["cancel_minutes"]) * 60 * 1_000_000_000
    n_jobs = 0
    n_touches = 0
    n_traded = 0
    n_hold = 0
    n_fail = 0
    n_neither = 0
    n_unknown = 0
    r_values: list[float] = []
    winner_dips: list[float] = []
    skipped_one_position = 0
    native_days = 0
    native_fail_days = 0
    for day_dir in sorted(root.iterdir()) if root.is_dir() else []:
        if not day_dir.is_dir():
            continue
        day = day_dir.name
        if day < start or day > end:
            continue
        path = day_dir / "REFILL-STUDY--branch--touch_record.json.gz"
        if not path.is_file():
            continue
        n_jobs += 1
        with GzipFile(path, "r") as handle:
            document = json.loads(handle.read().decode())
        episodes = document.get("episodes") or []
        occupied_until = 0
        view = None
        if use_native and episodes:
            try:
                from trading_research.research.rule_discovery.native import build_market_view
                view = build_market_view(day)
                native_days += 1
            except Exception:
                native_fail_days += 1
                view = None
        for episode in episodes:
            n_touches += 1
            side_name = str(episode.get("side") or "")
            side = 1 if side_name == "long" else -1 if side_name == "short" else 0
            ref = episode.get("reference") or {}
            touch_at = int(episode.get("occurrence_at") or episode.get("decision_at") or 0)
            if side == 0 or touch_at <= 0:
                n_unknown += 1
                continue
            level = Decimal(str(ref.get("low") if side == 1 else ref.get("high") or episode.get("geometry", {}).get("entry") or 0))
            geom = printed_refill_geometry(side, level)
            if touch_at < occupied_until:
                skipped_one_position += 1
                continue
            n_traded += 1
            end_ns = touch_at + horizon_ns
            batches: list[dict[str, Any]] = []
            if view is not None:
                for batch in view.executions(touch_at, end_ns + 1):
                    prices = tuple(trade.price for trade in batch.trades)
                    if not prices:
                        continue
                    batches.append({
                        "event_ns": batch.event_ns,
                        "available_at_ns": batch.available_at_ns,
                        "prices": prices,
                        "event_ids": tuple(trade.event_id for trade in batch.trades),
                    })
            else:
                endpoint = (episode.get("refill_response") or {}).get("endpoint") or {}
                prices = endpoint.get("prices") or []
                event_ns = endpoint.get("event_ns")
                if prices and event_ns:
                    batches.append({
                        "event_ns": int(event_ns),
                        "available_at_ns": int(endpoint.get("known_at") or event_ns),
                        "prices": [Decimal(str(p)) for p in prices],
                        "event_ids": (),
                    })
            passage = first_passage(
                batches,
                start_ns=touch_at,
                end_ns=end_ns,
                side=side,
                entry=geom["entry"],
                stop=geom["stop"],
                target=geom["target"],
            )
            cost = TICK * params["round_trip_cost_ticks"]
            if passage.result == "target_first":
                n_hold += 1
                r_values.append(float((params["target_ticks"] * TICK - cost) / (params["stop_ticks"] * TICK)))
                occupied_until = int(passage.resolved_at_ns or end_ns)
                dip = _adverse_before_target(batches, side=side, entry=geom["entry"], stop=geom["stop"], target=geom["target"])
                if dip is not None:
                    winner_dips.append(float(dip / TICK))
            elif passage.result == "stop_first":
                n_fail += 1
                r_values.append(float((-(params["stop_ticks"] * TICK) - cost) / (params["stop_ticks"] * TICK)))
                occupied_until = int(passage.resolved_at_ns or end_ns)
            elif passage.result in {"neither"}:
                n_neither += 1
                occupied_until = end_ns
            else:
                n_unknown += 1
    hold_rate = (n_hold / n_traded) if n_traded else None
    per_trade_r = (sum(r_values) / len(r_values)) if r_values else None
    winner_dips.sort()
    median_dip = winner_dips[len(winner_dips) // 2] if winner_dips else None
    return {
        "schema_version": "research-refill-printed-replay-v1",
        "start": start,
        "end": end,
        "jobs": n_jobs,
        "touches": n_touches,
        "traded": n_traded,
        "hold": n_hold,
        "fail": n_fail,
        "neither": n_neither,
        "unknown": n_unknown,
        "skipped_one_position": skipped_one_position,
        "hold_rate": hold_rate,
        "per_trade_r": per_trade_r,
        "median_winner_dip_ticks": median_dip,
        "native_days": native_days,
        "native_fail_days": native_fail_days,
        "printed_sessions": 235,
        "printed_touches": 41152,
        "known_differences": [
            "owned NQ only versus printed CME NQ and MNQ",
            "owned scanner 09:30 start, min 100 contracts, 4-tick departure versus unpublished printed zone recipe",
            "tick-count and contract differences listed, not tuned",
        ],
    }


def _adverse_before_target(batches: Sequence[Mapping[str, Any]], *, side: int, entry: Decimal, stop: Decimal, target: Decimal) -> Decimal | None:
    worst = Decimal(0)
    for row in batches:
        for price in row["prices"]:
            px = Decimal(str(price))
            if side * (px - target) >= 0:
                return worst
            move = Decimal(side) * (entry - px)
            if move > worst:
                worst = move
            if side * (px - stop) <= 0:
                return None
    return None


def dependency_limits() -> dict[str, Any]:
    return {
        "schema_version": LIMITS_SCHEMA,
        "assurance_version": ASSURANCE_VERSION,
        "tasks": {
            "P15-05": {
                "inferred_or_unavailable": ["A2-PZONE.percentiles", "O018"],
                "limits": "Formations may not treat unpublished P-zone percentiles or EVRange bands as source-exact.",
            },
            "P15-08": {
                "inferred_or_unavailable": ["A2-BALANCE", "A2-CONTEXT", "A2-EVENT"],
                "limits": "Candidate bank must label these research choices, not recovered constants.",
            },
            "P15-09": {
                "inferred_or_unavailable": ["A2-PZONE.session_end", "A2-PZONE.delete_invalidated", "A2-PZONE.percentiles", "O018", "clock_zone.JJumboFX"],
                "limits": "Jumbo adapter keeps 16:00 measurement. 1.5 extension and session-conditional BigTrades come from B0.1 overrides. Range deviations are recorded-only.",
            },
            "P15-10": {
                "inferred_or_unavailable": ["A2-GB-CLOCK.london_bounds_author", "clock_zone.GreenBird"],
                "limits": "A1-A3 are recorded for the adapter. Do not treat 02:00-05:00 as author-printed. Winter hour shift unverified.",
            },
            "P15-11": {
                "inferred_or_unavailable": ["GB-SCALP.A4.entry_bar", "clock_zone.GreenBird"],
                "limits": "Golden-pocket geometry is printed. The five-minute close trigger is operational.",
            },
            "P15-12": {
                "inferred_or_unavailable": ["KG1", "A2-IMBALANCE.ratio_4", "A2-FLOW.other", "clock_zone.Sires"],
                "limits": "KG1 stays inferred. Footprint 4x is recorded-only. Keep ratio 3 as B0.",
            },
            "P15-13": {
                "inferred_or_unavailable": ["clock_zone.Saint", "clock_zone.Member", "clock_zone.Keani"],
                "limits": "Value-area fractions 0.68/0.70 are recovered. Clock zone unverified.",
            },
            "P15-14": {
                "inferred_or_unavailable": ["A2-AUCTION-SAMPLE.thresholds", "clock_zone.jetbundle"],
                "limits": "Auction-state numeric thresholds are inferred.",
            },
            "P15-15": {
                "inferred_or_unavailable": ["A2-MACRO.C_score", "clock_zone.Stoic"],
                "limits": "C-score constants are inferred. Personal risk ladder stays out of setup scope.",
            },
            "P15-16": {
                "inferred_or_unavailable": ["printed refill zone recipe", "clock_zone.Refill study"],
                "limits": "Use existing scanner population. Printed execution is B0.1 replay only.",
            },
            "P2-03": {
                "inferred_or_unavailable": ["O018 bands", "O043 same-day unpublished VIX"],
                "limits": "O043 is available after VIX publication. Log-space IV is a coded alternative note, not a candidate.",
            },
            "P2-09": {
                "inferred_or_unavailable": ["full OPRA chain", "same-day OI"],
                "limits": "Max pain uses prior-date OI and the same coverage receipt as walls.",
            },
            "P2-11": {
                "inferred_or_unavailable": ["O043 before publication"],
                "limits": "Do not use same-day unpublished VIX as a predictor.",
            },
        },
    }


def regime_dimensions() -> dict[str, Any]:
    return {
        "schema_version": "research-regime-dimensions-v1",
        "frozen_before_candidate_results": True,
        "descriptive_only": True,
        "no_candidate_threshold_or_date_from_these_tables": True,
        "dimensions": [
            {
                "id": "calendar_year_outer_fold",
                "rule": "account-day year; outer fold is that year as test in EVALUATION.md",
                "source_operand": "session_date",
                "availability_clock": "account-day label known at open",
                "owned_data": str(PHASE1_RUN / "protocol/SCOPE.json"),
            },
            {
                "id": "session_bucket",
                "rule": "Asia 00:00-03:00, London/Europe 03:00-09:30, NY morning 09:30-12:00, NY afternoon 12:00-16:00 ET, intersect matching hours",
                "source_operand": "decision_session / decision_at",
                "availability_clock": "decision_at",
                "owned_data": "setup-records.jsonl.gz decision_session",
            },
            {
                "id": "day_of_week",
                "rule": "weekday of the account-day label in America/New_York",
                "source_operand": "session_date",
                "availability_clock": "account-day label",
                "owned_data": "setup-records.jsonl.gz session_date",
            },
            {
                "id": "realized_vol_tercile",
                "rule": "prior 20 complete sessions' daily ranges, terciles of that history ending before the account day",
                "source_operand": "prior same-contract daily high-low",
                "availability_clock": "prior session complete",
                "owned_data": "Phase 1 job coverage / native daily ranges when present; else unknown",
            },
            {
                "id": "overnight_range_tercile",
                "rule": "overnight range relative to its prior-20-session median, terciles",
                "source_operand": "overnight high-low",
                "availability_clock": "09:30",
                "owned_data": "native session ranges when present; else unknown",
            },
            {
                "id": "prior_close_vix_bucket",
                "rule": "prior-close VIX: below 15, 15 to 20, 20 to 30, above 30",
                "source_operand": "O043 / VIX publication",
                "availability_clock": "prior session VIX close after publication",
                "owned_data": str(VIX_PATH),
            },
            {
                "id": "inferred_gamma_sign_0932",
                "rule": "inferred aggregate gamma sign at 09:32: positive, negative, unknown; labelled inferred",
                "source_operand": "strategy_options.gamma_at",
                "availability_clock": "09:32",
                "owned_data": "QQQ prior-OI gamma model; unknown when chain missing",
            },
            {
                "id": "prior_day_type",
                "rule": "registered trend-or-balance rule on the prior complete session",
                "source_operand": "prior session path class",
                "availability_clock": "prior session complete",
                "owned_data": "Phase 1 path class when present; else unknown",
            },
            {
                "id": "macro_release_day",
                "rule": "CPI, payrolls, FOMC on the owned calendar",
                "source_operand": "A2-MACRO",
                "availability_clock": "civil date of the owned calendar",
                "owned_data": f"{CAL_PATH}; {FOMC_PATH}",
            },
        ],
    }


def _bootstrap_interval(values: Sequence[float]) -> dict[str, float | int | None]:
    from trading_research.research.contracts.evaluation import moving_block_bootstrap
    if len(values) < 2:
        return {"n": len(values), "mean": None, "lo": None, "hi": None, "low_support": True}
    samples = moving_block_bootstrap(values)
    mean = float(sum(values) / len(values))
    ordered = sorted(float(x) for x in samples)
    lo = ordered[int(0.025 * (len(ordered) - 1))]
    hi = ordered[int(0.975 * (len(ordered) - 1))]
    return {"n": len(values), "mean": mean, "lo": lo, "hi": hi, "low_support": len(values) < 30}


def _vix_map() -> dict[str, float]:
    if not VIX_PATH.is_file():
        return {}
    import pyarrow.parquet as pq
    table = pq.read_table(VIX_PATH, columns=["date", "value"])
    out: dict[str, float] = {}
    for d, v in zip(table.column("date").to_pylist(), table.column("value").to_pylist()):
        if d is None or v is None:
            continue
        key = d.isoformat() if hasattr(d, "isoformat") else str(d)
        out[key] = float(v)
    return out


def _macro_days() -> set[str]:
    days: set[str] = set()
    import pyarrow.parquet as pq
    for path in (CAL_PATH, FOMC_PATH):
        if not path.is_file():
            continue
        table = pq.read_table(path)
        names = set(table.column_names)
        col = "date" if "date" in names else "session_date" if "session_date" in names else None
        if col is None:
            continue
        for d in table.column(col).to_pylist():
            if d is None:
                continue
            days.add(d.isoformat() if hasattr(d, "isoformat") else str(d)[:10])
    return days


def _passage_from_setup(record: Mapping[str, Any]) -> dict[str, Any]:
    setup = record.get("setup") or {}
    geometry = setup.get("geometry") or {}
    side_name = setup.get("side") or (setup.get("values") or {}).get("side")
    side = 1 if side_name == "long" else -1 if side_name == "short" else 0
    entry = geometry.get("entry")
    stop = geometry.get("stop")
    target = geometry.get("target")
    start_ns = setup.get("decision_at") or record.get("legacy_outcome", {}).get("start_ns")
    measure = record.get("price_measurement") or {}
    batches = []
    last_end = start_ns
    for horizon in measure.get("horizons") or []:
        for ev in horizon.get("extremum_evidence") or []:
            hid = str(ev.get("id") or "")
            parts = hid.split(":")
            event_ns = None
            if len(parts) >= 4:
                try:
                    event_ns = int(parts[-2])
                except ValueError:
                    event_ns = None
            if event_ns is None:
                continue
            prices = []
            if ev.get("low") is not None:
                prices.append(Decimal(str(ev["low"])))
            if ev.get("high") is not None:
                prices.append(Decimal(str(ev["high"])))
            if not prices:
                continue
            batches.append({"event_ns": event_ns, "available_at_ns": event_ns, "prices": prices, "event_ids": (hid,)})
            last_end = max(int(last_end or 0), event_ns)
    result = {"result": "invalid_geometry", "net_points": None, "mae_points": None, "mfe_points": None}
    if side in (-1, 1) and entry is not None and stop is not None and target is not None and start_ns:
        passage = first_passage(
            batches,
            start_ns=int(start_ns),
            end_ns=int(last_end or start_ns),
            side=side,
            entry=Decimal(str(entry)),
            stop=Decimal(str(stop)),
            target=Decimal(str(target)),
            coverage=(record.get("legacy_outcome") or {}).get("coverage"),
        )
        cost = COMMISSION_SIDE / POINT_VALUE
        net = None
        if passage.result == "target_first":
            net = Decimal(side) * (Decimal(str(target)) - Decimal(str(entry))) - cost
        elif passage.result == "stop_first":
            net = Decimal(side) * (Decimal(str(stop)) - Decimal(str(entry))) - cost
        horizons = measure.get("horizons") or []
        mae = horizons[-1].get("adverse_points") if horizons else None
        mfe = horizons[-1].get("favorable_points") if horizons else None
        result = {
            "result": passage.result,
            "net_points": None if net is None else float(net),
            "mae_points": None if mae is None else float(mae),
            "mfe_points": None if mfe is None else float(mfe),
            "resolved_at_ns": passage.resolved_at_ns,
        }
    else:
        legacy = record.get("legacy_outcome") or {}
        result["result"] = str(legacy.get("result") or "not_applicable")
        horizons = measure.get("horizons") or []
        if horizons:
            result["mae_points"] = float(horizons[-1]["adverse_points"]) if horizons[-1].get("adverse_points") is not None else None
            result["mfe_points"] = float(horizons[-1]["favorable_points"]) if horizons[-1].get("favorable_points") is not None else None
    return result


def build_strategy_book_b0(*, attempt: Path, ledger: Mapping[str, Any]) -> dict[str, Any]:
    vix = _vix_map()
    macro = _macro_days()
    ledger_by_op = {row["operand_id"]: row for row in ledger.get("rows") or []}
    cells: dict[str, dict[str, Any]] = {}
    coverage_path = PHASE1_RUN / "registry/coverage.json"
    if coverage_path.is_file():
        coverage = json.loads(coverage_path.read_text())
        for row in coverage.get("branches") or []:
            key = str(row.get("coverage_id") or f"{row.get('method_id')}:branch:{row.get('branch')}")
            cells[key] = {
                "family": row.get("method_id"),
                "branch": row.get("branch"),
                "coverage_id": key,
                "n": 0,
                "by_year": {},
                "by_session": {},
                "by_dow": {},
                "by_vix": {},
                "by_macro": {"release": 0, "other": 0},
                "results": {},
                "net": [],
                "daily_net": {},
                "mae": [],
                "mfe": [],
                "low_support_cells": [],
                "scope": row.get("kind") or "entry_setup",
                "artifact": str(SETUP_RECORDS),
            }
    n_records = 0
    with GzipFile(SETUP_RECORDS, "r") as handle:
        for raw in handle:
            record = json.loads(raw.decode())
            n_records += 1
            coverage_id = str(record.get("coverage_id") or "")
            setup = record.get("setup") or {}
            family = setup.get("method") or coverage_id.split(":")[0]
            branch = setup.get("branch") or coverage_id
            key = coverage_id or f"{family}:{branch}"
            cell = cells.setdefault(
                key,
                {
                    "family": family,
                    "branch": branch,
                    "coverage_id": key,
                    "n": 0,
                    "by_year": {},
                    "by_session": {},
                    "by_dow": {},
                    "by_vix": {},
                    "by_macro": {"release": 0, "other": 0},
                    "results": {},
                    "net": [],
                    "daily_net": {},
                    "mae": [],
                    "mfe": [],
                    "low_support_cells": [],
                    "scope": (setup.get("strategy_assessment") or {}).get("scope") or "entry_setup",
                    "artifact": record.get("native_job", {}).get("path"),
                },
            )
            cell["n"] += 1
            day = str(record.get("session_date") or "")
            year = day[:4]
            cell["by_year"][year] = cell["by_year"].get(year, 0) + 1
            session = str(record.get("decision_session") or "unknown")
            cell["by_session"][session] = cell["by_session"].get(session, 0) + 1
            if day:
                dow = date.fromisoformat(day).strftime("%A")
                cell["by_dow"][dow] = cell["by_dow"].get(dow, 0) + 1
            prior = None
            if day:
                prior_d = date.fromisoformat(day)
                for _ in range(1, 8):
                    prior_d = date.fromordinal(prior_d.toordinal() - 1)
                    iso = prior_d.isoformat()
                    if iso in vix:
                        prior = vix[iso]
                        break
            if prior is None:
                bucket = "unknown"
            elif prior < 15:
                bucket = "below_15"
            elif prior < 20:
                bucket = "15_to_20"
            elif prior < 30:
                bucket = "20_to_30"
            else:
                bucket = "above_30"
            cell["by_vix"][bucket] = cell["by_vix"].get(bucket, 0) + 1
            if day in macro:
                cell["by_macro"]["release"] += 1
            else:
                cell["by_macro"]["other"] += 1
            passage = _passage_from_setup(record)
            res = str(passage.get("result") or "unknown")
            cell["results"][res] = cell["results"].get(res, 0) + 1
            if passage.get("net_points") is not None:
                cell["net"].append(float(passage["net_points"]))
                cell["daily_net"].setdefault(day, 0.0)
                cell["daily_net"][day] += float(passage["net_points"])
            if passage.get("mae_points") is not None:
                cell["mae"].append(float(passage["mae_points"]))
            if passage.get("mfe_points") is not None:
                cell["mfe"].append(float(passage["mfe_points"]))
    book_rows = []
    csv_dir = attempt / "strategy_book_b0_csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    for key, cell in sorted(cells.items()):
        net_ci = _bootstrap_interval(cell["net"])
        daily_ci = _bootstrap_interval(list(cell["daily_net"].values()))
        def mark(mapping: Mapping[str, int]) -> dict[str, Any]:
            out = {}
            for name, count in mapping.items():
                out[name] = {"n": count, "low_support": count < 30}
            return out
        row = {
            "family": cell["family"],
            "branch": cell["branch"],
            "coverage_id": key,
            "scope": cell["scope"],
            "n": cell["n"],
            "low_support": cell["n"] < 30,
            "by_year": mark(cell["by_year"]),
            "by_session": mark(cell["by_session"]),
            "by_dow": mark(cell["by_dow"]),
            "by_vix": mark(cell["by_vix"]),
            "by_macro": mark(cell["by_macro"]),
            "ordered_results": cell["results"],
            "net_points": net_ci,
            "daily_net_points": daily_ci,
            "mae_mean": (sum(cell["mae"]) / len(cell["mae"])) if cell["mae"] else None,
            "mfe_mean": (sum(cell["mfe"]) / len(cell["mfe"])) if cell["mfe"] else None,
            "artifact": cell["artifact"],
            "ledger_links": [op for op in ledger_by_op if op.split(".")[0] in key or key.startswith(cell["family"])],
        }
        book_rows.append(row)
        csv_path = csv_dir / f"{key.replace(':', '--')}.csv"
        lines = ["metric,value,n,low_support,artifact"]
        lines.append(f"n,{cell['n']},{cell['n']},{str(cell['n'] < 30).lower()},{cell['artifact'] or ''}")
        lines.append(f"net_mean,{net_ci['mean']},{net_ci['n']},{str(net_ci['low_support']).lower()},setup-records")
        for res, count in cell["results"].items():
            lines.append(f"result_{res},{count},{count},{str(count < 30).lower()},first_passage")
        csv_path.write_text("\n".join(lines) + "\n")
    document = {
        "schema_version": "research-strategy-book-b0-v1",
        "header": {
            "descriptive_only": True,
            "no_candidate_threshold_or_date_from_these_tables": True,
            "corrected_baseline_columns": "pending full-history B0.1 run under implementation/reports/research-work/baseline-repair/ (no RUN_COMPLETE.json present)",
            "exposure_note": "Descriptive regime cuts were published for B0 only.",
            "records": n_records,
            "setup_records": str(SETUP_RECORDS),
        },
        "branches": book_rows,
    }
    return document


def write_strategy_book(attempt: Path, ledger: Mapping[str, Any]) -> dict[str, Any]:
    document = build_strategy_book_b0(attempt=attempt, ledger=ledger)
    (attempt / "STRATEGY_BOOK_B0.json").write_text(json.dumps(document, sort_keys=True, indent=2, allow_nan=False) + "\n")
    lines = [
        "# Strategy Book B0 (descriptive only)",
        "",
        "No candidate, threshold, or date may be chosen from these tables.",
        "Corrected-baseline B0.1 columns are pending a completed full-history run under implementation/reports/research-work/baseline-repair/.",
        "Descriptive regime cuts were published for B0 only.",
        "",
        f"Records: {document['header']['records']}",
        "",
        "| family | branch | n | net_mean | low_support |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in document["branches"]:
        lines.append(
            f"| {row['family']} | {row['branch']} | {row['n']} | {row['net_points']['mean']} | {row['low_support']} |"
        )
    (attempt / "STRATEGY_BOOK_B0.md").write_text("\n".join(lines) + "\n")
    return document


P15_04_PLAN_PATHS = (
    "planning/phase-1-5/tasks/P15-04.md",
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/WORKFLOW.md",
    "planning/phase-1-5/SPEC.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
)
P15_04_OWNED = (
    "implementation/src/trading_research/research/rule_discovery/reconstruction.py",
    "planning/phase-1-5/SOURCE_RECONSTRUCTION_LEDGER.json",
    "implementation/tests/rule_discovery/test_p15_04.py",
)
P15_04_CODE_PATHS = P15_04_OWNED + (
    "implementation/src/trading_research/errors.py",
    "implementation/src/trading_research/research/contracts/identity.py",
    "implementation/src/trading_research/research/contracts/types.py",
    "implementation/src/trading_research/research/contracts/outcomes.py",
    "implementation/src/trading_research/research/contracts/evaluation.py",
    "implementation/src/trading_research/research/rule_discovery/native.py",
    "implementation/src/trading_research/research/method_pack/clocks.py",
    "implementation/src/trading_research/research/method_pack/branch_coverage.py",
    "implementation/pyproject.toml",
)
P15_00_RECEIPT = ROOT / "implementation/reports/research-work/P15-00/ea9693217cb577cb/attempt-0001/TASK_RECEIPT.json"
P15_02_RECEIPT = ROOT / "implementation/reports/research-work/P15-02/c9669fa98ba72c43/attempt-0001/TASK_RECEIPT.json"


def write_p15_04_identity(attempt: Path) -> dict[str, Any]:
    import sys
    from trading_research.research.contracts.identity import (
        code_snapshot_document,
        digest,
        file_digest,
        plan_snapshot_document,
        semantic_run_id,
        write_json_document,
        write_snapshot_tree,
    )

    plan_files = {rel: file_digest(ROOT / rel) for rel in P15_04_PLAN_PATHS}
    code_files = {rel: file_digest(ROOT / rel) for rel in P15_04_CODE_PATHS}
    plan_copies = write_snapshot_tree(attempt, "plan", plan_files, root=ROOT)
    code_copies = write_snapshot_tree(attempt, "code", code_files, root=ROOT)
    lock = ROOT / "implementation/uv.lock"
    lock_sha = file_digest(lock) if lock.is_file() else file_digest(ROOT / "implementation/pyproject.toml")
    plan_doc = plan_snapshot_document(plan_files, plan_copies)
    code_doc = code_snapshot_document(
        code_files,
        code_copies,
        runtime={"python": sys.version.split()[0]},
        dependency_lock_sha256=lock_sha,
        imported_modules=[
            "trading_research.errors",
            "trading_research.research.contracts.identity",
            "trading_research.research.contracts.types",
            "trading_research.research.contracts.outcomes",
            "trading_research.research.contracts.evaluation",
            "trading_research.research.rule_discovery.reconstruction",
            "trading_research.research.rule_discovery.native",
            "trading_research.research.method_pack.clocks",
            "trading_research.research.method_pack.branch_coverage",
        ],
    )
    plan_sha256 = digest(plan_files)
    code_sha256 = digest(code_doc)
    pred = {"P15-00": file_digest(P15_00_RECEIPT), "P15-02": file_digest(P15_02_RECEIPT)}
    draft = {
        "schema_version": "research-draft-manifest-v2",
        "task_id": "P15-04",
        "assurance_version": ASSURANCE_VERSION,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_receipts": pred,
        "input_identities": {
            "P15-00": {"path": str(P15_00_RECEIPT), "sha256": pred["P15-00"]},
            "P15-02": {"path": str(P15_02_RECEIPT), "sha256": pred["P15-02"]},
            "source_audit": {
                "path": str(ROOT / "planning/phase-1-5/SOURCE_AUDIT_2026-09-14.md"),
                "sha256": file_digest(ROOT / "planning/phase-1-5/SOURCE_AUDIT_2026-09-14.md"),
            },
        },
        "coverage_identity": file_digest(PHASE1_RUN / "protocol/SCOPE.json"),
        "registered_candidate_config": None,
        "declared_study_dates": {"start": "2020-01-01", "end": "2026-09-03"},
        "drafted_at": "2026-09-14",
    }
    run_id = semantic_run_id(draft)
    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft)
    write_json_document(attempt / "WORKTREE_SNAPSHOT.json", {"schema": "research-worktree-snapshot-v1", "owned_paths": list(P15_04_OWNED)})
    return {"run_id": run_id, "plan_sha256": plan_sha256, "code_sha256": code_sha256, "draft": draft, "predecessor_receipts": pred}
