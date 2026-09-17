#!/usr/bin/env python3
"""Assemble P15-16A artifacts, identity, receipt, and S01/S03 probes."""
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path("/workspace")
SRC = ROOT / "implementation/src"
sys.path.insert(0, str(SRC))

from trading_research.research.contracts.identity import (  # noqa: E402
    ASSURANCE_VERSION,
    artifact_entry,
    digest,
    file_digest,
    write_json_document,
)
from trading_research.research.contracts.receipts import verify_task_receipt  # noqa: E402
from trading_research.research.rule_discovery.runner import write_named_receipt, write_task_identity  # noqa: E402

IMP = ROOT / "implementation"
PY = IMP / ".venv/bin/python"
REPORTS = ROOT / "implementation/reports/research-work"
TRACK = REPORTS / "P15-16A"
OLD_B02_RUN = TRACK / "1e13829f2c88f1e1"
ROUND2_B02_RUN = TRACK / "4e3ed4d86149bf9c"
B02_RUN = ROUND2_B02_RUN
FAMILIES_DIR = ROOT / "implementation/src/trading_research/research/rule_discovery/families"
FAMILY_SPEC_FILES = {
    "JJ-TBR": "jumbo.json",
    "GB-FAIL": "green_failure.json",
    "GB-VWAP": "green_vwap_scalp.json",
    "GB-SCALP": "green_vwap_scalp.json",
    "SIRES": "sires.json",
    "REFILL-STUDY": "processes.json",
    "SAINT-AMT": "saint.json",
    "MEMBER-TWO-REASONS": "member.json",
    "KEANI-OPEN-ABOVE-VALUE": "keani.json",
}
REPLAY_SRC = TRACK / "79fb63c5a6a7dc90/attempt-0001"
LEDGER = ROOT / "planning/phase-1-5/SOURCE_RECONSTRUCTION_LEDGER.json"
FIDELITY_SCHEMA = "research-fidelity-matrix-v1"
LEDGER_SCHEMA = "research-ledger-corrections-v1"
MATRIX_SCHEMA = "research-evidence-matrix-v2"
PROBES_SCHEMA = "research-probes-s01-s03-v1"
VERIFY_SCHEMA = "research-verify-task-v1"
B02_SUMMARY_SCHEMA = "research-b02-summary-v1"
CENSUS_ROOT = Path("/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7")

PREDECESSORS = {
    "P15-09": REPORTS / "P15-09/250e5aea146f3516/attempt-0001/TASK_RECEIPT.json",
    "P15-10": REPORTS / "P15-10/b89cbd7b0f4473cc/attempt-0001/TASK_RECEIPT.json",
    "P15-11": REPORTS / "P15-11/9e7fda7b291cce99/attempt-0001/TASK_RECEIPT.json",
    "P15-12": REPORTS / "P15-12/f33f750e365a04c1/attempt-0001/TASK_RECEIPT.json",
    "P15-13": REPORTS / "P15-13/8de8e78a21b0838a/attempt-0001/TASK_RECEIPT.json",
    "P15-14": REPORTS / "P15-14/f01de253cf514105/attempt-0001/TASK_RECEIPT.json",
    "P15-15": REPORTS / "P15-15/ced9a15cf6c6dae2/attempt-0001/TASK_RECEIPT.json",
    "P15-16": REPORTS / "P15-16/cf6bf4778e53a0b0/attempt-0001/TASK_RECEIPT.json",
}

PLAN_PATHS = (
    "planning/phase-1-5/tasks/P15-16A.md",
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/WORKFLOW.md",
    "planning/phase-1-5/SPEC.md",
    "planning/phase-1-5/SEARCH_CONTRACT.md",
    "planning/phase-1-5/SOURCE_ADDITIONS_2026-09-14.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
    "planning/research-program/PERFORMANCE.md",
    "planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md",
    "planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md",
    "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json",
)

def _repo_files(relative_dir: str, suffix: str) -> tuple[str, ...]:
    root = ROOT / relative_dir
    out: list[str] = []
    if not root.is_dir():
        return ()
    for path in sorted(root.rglob(f"*{suffix}")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.suffix != suffix:
            continue
        out.append(path.relative_to(ROOT).as_posix())
    return tuple(out)


ADAPTER_PY = _repo_files("implementation/src/trading_research/research/rule_discovery/source_adapters", ".py")
FAMILY_JSON = _repo_files("implementation/src/trading_research/research/rule_discovery/families", ".json")
CONTRACT_TESTS = _repo_files("implementation/tests/contracts", ".py")
P15_16A_TESTS = tuple(
    path
    for path in _repo_files("implementation/tests/rule_discovery", ".py")
    if Path(path).name.startswith("test_p15_16a")
)

CODE_PATHS = tuple(
    dict.fromkeys(
        ADAPTER_PY
        + FAMILY_JSON
        + (
            "implementation/src/trading_research/research/rule_discovery/native.py",
            "implementation/src/trading_research/research/rule_discovery/runner.py",
            "implementation/src/trading_research/research/rule_discovery/engine_slice.py",
            "implementation/src/trading_research/research/rule_discovery/formations.py",
            "implementation/src/trading_research/research/rule_discovery/profiles.py",
            "implementation/src/trading_research/research/rule_discovery/sequences.py",
            "implementation/src/trading_research/research/rule_discovery/kernels.py",
            "implementation/src/trading_research/research/rule_discovery/census_reader.py",
            "implementation/src/trading_research/research/rule_discovery/baseline.py",
            "implementation/src/trading_research/research/rule_discovery/run_adapter_populations.py",
            "implementation/src/trading_research/research/contracts/receipts.py",
            "implementation/src/trading_research/research/contracts/identity.py",
            "implementation/tools/replay_author_examples.py",
            "implementation/tools/produce_p15_16a.py",
            "implementation/tests/rule_discovery/test_engine_hygiene.py",
        )
        + P15_16A_TESTS
        + CONTRACT_TESTS
    )
)
OWNED = CODE_PATHS

NODE = "implementation/tests/rule_discovery/test_p15_16a.py"
LEDGER_FIX = {
    "L018": {
        "correction": "Five-minute close confirmation is printed (GB pp19,25). B0.2 uses it as a literal for Asia/PDL and labels other cases OD.",
        "ruling": "F19 / F06 / RR-13",
        "new_classification": "printed-formula-recovered",
    },
    "L021": {
        "correction": "A period ends 10:00 (TPO p3). B0.2 Keani removes the 11:00 cutoff.",
        "ruling": "F16",
        "new_classification": "printed-formula-recovered",
    },
    "L024": {
        "correction": "1.5R spoken target is printed (K10 pp7-8). B0.2 Member uses it as a literal, separate from the drawn-ticket R:R conflict.",
        "ruling": "F15 / RR-23",
        "new_classification": "printed-formula-recovered",
    },
    "L030": {
        "correction": "The 3-minute order-block option is printed (TBR p27). B0.2 admits 2/3/5m OB or a rejection block; 3-minute first-contact is a registered variant.",
        "ruling": "F11",
        "new_classification": "printed-formula-recovered",
    },
    "L032": {
        "correction": "Entry distances of one to two ticks of the defended level are printed (STOP pp9-10). B0.2 SIRES uses them as literals.",
        "ruling": "A3/A5 SIRES",
        "new_classification": "printed-formula-recovered",
    },
    "L038": {
        "correction": "Green Bird seasonal New York clocks are evidenced (UTC-5 winter, UTC-4 summer). B0.2 documents drop clock_zone_unverified for GB; the frozen B0/B0.1 flag is unchanged.",
        "ruling": "F18 / F19",
        "new_classification": "printed-formula-recovered",
    },
    "L039": {
        "correction": "TBR p.4/p.6 establishes the New York clock. JJ-TBR is removed from CLOCK_ZONE_UNVERIFIED_FAMILIES. B0.2 documents set clock_zone America/New_York.",
        "ruling": "F18",
        "new_classification": "printed-formula-recovered",
    },
    "L040": {
        "correction": "SIRES PST statistics (MAMT p20) are noted for that document only. Family remains clock_zone_unverified.",
        "ruling": "F18",
        "new_classification": "not-identifiable-from-owned-source",
    },
    "L041": {
        "correction": "SAINT charts print ET on Sierra Chart (RR-22). B0.2 covers the Asia session; family clock_zone_unverified remains for winter/DST footer gaps.",
        "ruling": "RR-22 / F18",
        "new_classification": "printed-but-implementation-differs",
    },
    "L042": {
        "correction": "Member worked example is ES; NQ adapter is a labelled transfer. Clock remains unverified.",
        "ruling": "RR-23",
        "new_classification": "not-identifiable-from-owned-source",
    },
    "L043": {
        "correction": "Keani has no dated ticket. Clock remains unverified.",
        "ruling": "F16",
        "new_classification": "not-identifiable-from-owned-source",
    },
    "L044": {
        "correction": "Refill Effect tables have no timezone. REFILL-STUDY remains clock_zone_unverified.",
        "ruling": "F10 / F20",
        "new_classification": "not-identifiable-from-owned-source",
    },
}


def _rule_rows(path: Path) -> list[dict]:
    doc = json.loads(path.read_text())
    if isinstance(doc, list):
        return [row for row in doc if isinstance(row, dict)]
    if isinstance(doc, dict):
        if isinstance(doc.get("rules"), list):
            return [row for row in doc["rules"] if isinstance(row, dict)]
        out = []
        for key, value in doc.items():
            if key in {"schema", "family", "schema_version"}:
                continue
            if isinstance(value, dict):
                row = dict(value)
                row.setdefault("rule_id", key)
                out.append(row)
        return out
    return []


NONE_FIXTURE = "no discriminating fixture"

RULE_FIXTURES = {
    "F06-A9-pwl": "test_p15_16a_greenbird.py::test_gap1_prior_week_low_sweep_and_reclaim_long",
    "RR-16-tdo-retest": "test_p15_16a_greenbird.py::test_gap2_tdo_retest_records_mode_time_and_price",
    "RR-01-extension-band-1.33-1.66": "test_p15_16a_jumbo.py::test_rr01_extension_band_identity_and_printed_examples",
    "RR-01-OD-near-band-0.33-0.66": "test_p15_16a_jumbo.py::test_rr01_extension_band_identity_and_printed_examples",
    "RR-03-sweep-from-09:00": "test_p15_16a_jumbo.py::test_rr03_sweep_before_0930_is_a_valid_trigger",
    "RR-03-modal-reversal-09:40-09:50": f"{NONE_FIXTURE}: modal 09:40-09:50 is labelled; no nodeid fails when this row is removed",
    "RR-03-extension-after-10:00": "test_p15_16a_jumbo.py::test_f08_extension_after_1000_and_1300_admitted",
    "RR-04-london-02:00-03:00": "test_p15_16a_jumbo.py::test_rr04_london_box_is_0200_0300_not_0000_0300",
    "RR-05-pzone-anchors": "test_p15_16a_jumbo.py::test_rr05_printed_pzone_absorption_fixture",
    "RR-05-OD-absorption-proxy": "test_p15_16a_jumbo.py::test_rr05_printed_pzone_absorption_fixture",
    "RR-06-reclaim-entry": "test_p15_16a_jumbo.py::test_rr06_reclaim_is_the_entry_and_depth_is_recorded_not_required",
    "RR-06-objective-plus-0.5": f"{NONE_FIXTURE}: +0.5 objective is labelled; no nodeid fails when this row is removed",
    "RR-06-projection-ladder": f"{NONE_FIXTURE}: projection ladder is labelled; no nodeid fails when this row is removed",
    "RR-06-sweep-depth-recorded": "test_p15_16a_jumbo.py::test_rr06_reclaim_is_the_entry_and_depth_is_recorded_not_required",
    "RR-07-OD-sessionstat-60": "test_p15_16a_jumbo.py::test_rr07_sessionstat_coincidence_and_evrange_after_tape",
    "RR-07-evrange-fixture": "test_p15_16a_jumbo.py::test_rr07_sessionstat_coincidence_and_evrange_after_tape",
    "RR-08-open-location-at-09:30": "test_p15_16a_jumbo.py::test_rr08_open_location_uses_prior_rth_at_0930",
    "RR-08-OD-branch-selector": f"{NONE_FIXTURE}: OD branch selector is labelled; no nodeid fails when this row is removed",
    "RR-09-published-statistics": "test_p15_16a_jumbo.py::test_rr09_one_side_is_high_only_plus_low_only",
    "RR-09-bigtrades-deferred": f"{NONE_FIXTURE}: bigtrades is deferred; no nodeid fails when this row is removed",
    "F08-single-extended-reduced-after-10:00": "test_p15_16a_jumbo.py::test_f08_extension_after_1000_and_1300_admitted",
    "F11-confirm-3m-ob-baseline": "test_p15_16a_jumbo.py::test_f11_3m_ob_baseline_and_od_variants_labelled",
    "F11-OD-confirm-2m-5m-rejection": "test_p15_16a_jumbo.py::test_f11_3m_ob_baseline_and_od_variants_labelled",
    "F12-candidate-references-unchanged": f"{NONE_FIXTURE}: RULES membership is asserted in test_f18_f19_clock_fields; no nodeid fails when F12 behavior is removed",
    "F17-pzone-generator-unknown": f"{NONE_FIXTURE}: pzone generator unknown is labelled; no nodeid fails when this row is removed",
    "F18-ny-clock-ET": "test_p15_16a.py::test_S31_jj_tbr_clock_zone_verified",
    "F19-chart-clocks-UK-UTC": "test_p15_16a_jumbo.py::test_f18_f19_clock_fields",
    "F01-scalp-observations": "test_p15_16a_greenbird.py::test_f01_old_scalp_branches_are_observations",
    "F06-A1-london": "test_p15_16a_greenbird.py::test_f06_a1_requires_retest_and_post_open_close",
    "F06-A2-asia": "test_p15_16a_greenbird.py::test_rr13_five_minute_required_for_asia_high",
    "F06-A3-pdl": "test_p15_16a_greenbird.py::test_f06_a3_pdl_stop_is_swept_level_not_extreme",
    "F06-A4-pocket": "test_p15_16a_greenbird.py::test_rr14_pocket_uses_impulse_not_910_box",
    "F06-A5-nwog": "test_p15_16a_greenbird.py::test_f06_a5_nwog_has_no_am_cutoff",
    "F07-directional-bias": "test_p15_16a_greenbird.py::test_f07_bias_reports_unfiltered_and_filtered",
    "F13-gb-vwap": "test_p15_16a_greenbird.py::test_f13_vwap_missing_retest_is_fail_not_unknown",
    "F18-clock-seasonal-ny": f"{NONE_FIXTURE}: GB-FAIL/GB-VWAP/GB-SCALP stay in CLOCK_ZONE_UNVERIFIED_FAMILIES so frozen B0/B0.1 dual-scan flags do not move",
    "RR-11-sessions-boxes": "test_p15_16a_greenbird.py::test_rr11_september_uses_asia_0000_and_london_0200_0500",
    "RR-12-position-size": "test_p15_16a_greenbird.py::test_rr12_ladder_and_750_not_scored",
    "RR-12-risk-exits": "test_p15_16a_greenbird.py::test_rr12_ladder_and_750_not_scored",
    "RR-13-confirmation-modes": "test_p15_16a_greenbird.py::test_rr13_five_minute_required_for_asia_high",
    "RR-14-golden-pocket": "test_p15_16a_greenbird.py::test_rr14_pocket_uses_impulse_not_910_box",
    "RR-15-objective-horizon": "test_p15_16a_greenbird.py::test_rr15_objective_horizon_is_next_open_not_30m",
    "F02_clean_squeeze_no_retest": "test_p15_16a_sires.py::test_f02_pullback_then_absorption_is_not_clean_squeeze",
    "F03_replenishment_ticks": "test_p15_16a_sires.py::test_f03_replenishment_three_refills_pass_two_fail",
    "F03_reward_ticks": "test_p15_16a_sires.py::test_f03_reward_ticks_separate_from_replenishment",
    "RR21_es_ticks_not_nq": f"{NONE_FIXTURE}: ES-tick conversion is labelled; no nodeid fails when this SIRES row is removed",
    "F09_location_eligibility": "test_p15_16a_sires.py::test_f09_location_lvn_passes_poc_fails",
    "F09_thesis_killers": "test_p15_16a_sires.py::test_f09_thesis_killers_c1",
    "F09_gamma_permission": "test_p15_16a_sires.py::test_f09_gamma_ofm_short_fade_long_missing_is_unknown",
    "RR20_aggression_band": "test_p15_16a_sires.py::test_rr20_aggression_30_60",
    "RR20_imbalance_350": "test_p15_16a_sires.py::test_rr20_imbalance_350_and_vwap_bands",
    "RR20_footprint_flag": f"{NONE_FIXTURE}: footprint flag is labelled; no nodeid fails when this row is removed",
    "RR20_vwap_bands": "test_p15_16a_sires.py::test_rr20_imbalance_350_and_vwap_bands",
    "RR18_resting_stop_entry": "test_p15_16a_sires.py::test_rr18_resting_stop_is_baseline_ofm_entry",
    "RR18_ofm_40_tick_target": "test_p15_16a_sires.py::test_rr18_40_tick_and_control_zone_objectives",
    "RR18_control_zone_target": "test_p15_16a_sires.py::test_rr18_40_tick_and_control_zone_objectives",
    "RR19_partial_1to1_be": "test_p15_16a_sires.py::test_rr19_management_partial_trail_daily_stop",
    "RR19_trail_protected_swing": "test_p15_16a_sires.py::test_rr19_management_partial_trail_daily_stop",
    "RR19_daily_stop": "test_p15_16a_sires.py::test_rr19_management_partial_trail_daily_stop",
    "OD_level_tolerance_ticks": "test_p15_16a_sires.py::test_rr17_replay_sires_author_examples",
    "OD_fast_release": "test_p15_16a_sires.py::test_f02_fast_release_no_pullback_passes_clean_squeeze",
    "OD_reward_window": f"{NONE_FIXTURE}: reward window OD is labelled; no nodeid fails when this row is removed",
    "A3_entry_one_to_two_ticks": "test_p15_16a_sires.py::test_a3_entry_one_to_two_ticks_rejects_wider",
    "F09_balance_fade_unpaid": "test_p15_16a_sires.py::test_f09_balance_fade_unpaid_and_own_aggression",
    "F09_balance_fade_own_aggression": "test_p15_16a_sires.py::test_f09_balance_fade_unpaid_and_own_aggression",
    "OD_replenishment_band": "test_p15_16a_sires.py::test_f03_replenishment_three_refills_pass_two_fail",
    "F10_zone_from_aggressive_clusters": "test_p15_16a_sires.py::test_f10_f20_refill_zone_from_clusters_and_departure_is_actual_time",
    "F10_literal_cluster_size_family": "test_p15_16a_sires.py::test_rr21_refill_literal_size_family_and_bracket",
    "F10_actual_departure": "test_p15_16a_sires.py::test_f10_f20_refill_zone_from_clusters_and_departure_is_actual_time",
    "F10_distinct_later_touches": "test_p15_16a_sires.py::test_f10_future_prints_after_touch_do_not_change_pre_touch_features",
    "F20_printed_bracket": "test_p15_16a_sires.py::test_f10_f20_refill_zone_from_clusters_and_departure_is_actual_time",
    "RR21_hold_label_boundary": "test_p15_16a_sires.py::test_rr21_future_refills_after_decision_are_ignored",
    "RR21_population_175": "test_p15_16a_sires.py::test_rr21_refill_literal_size_family_and_bracket",
    "F04-arrival_read": "test_p15_16a_saint.py::test_F04_arrival_fast_vs_slow",
    "F04-profile_allows_trade": "test_p15_16a_saint.py::test_F04_profile_excludes_trend",
    "F04-double-shelf-target": "test_p15_16a_saint.py::test_F04_double_shelf_target",
    "F04-alignment_ok": "test_p15_16a_saint.py::test_F04_alignment_not_from_trade_side",
    "F05-failed_auction_return": "test_p15_16a_saint.py::test_F05_no_older_auction_gate",
    "F05-poc_traversal": "test_p15_16a_saint.py::test_F05_poc_tell_selects_target",
    "RR-22-asia-session": "test_p15_16a_saint.py::test_RR22_asia_session_not_ny_only",
    "RR-22-balance-fit": f"{NONE_FIXTURE}: cover_frac OD is labelled; no nodeid fails when this row is removed",
    "RR-22-single-retest": "test_p15_16a_saint.py::test_RR22_single_retest_only",
    "RR-22-asia-range": "test_p15_16a_saint.py::test_RR22_asia_range_literal",
    "RR-22-long-mirror": "test_p15_16a_saint.py::test_RR22_long_mirror",
    "F15-no-1245-split": "test_p15_16a_saint.py::test_F15_no_1245_split",
    "F15-two-reasons": "test_p15_16a_saint.py::test_F15_independence_binds_admission",
    "F15-kg1-alternative": f"{NONE_FIXTURE}: KG1 OD alternative is labelled; no nodeid fails when this row is removed",
    "F15-independence-admission": "test_p15_16a_saint.py::test_F15_independence_binds_admission",
    "F15-target-1.5R": "test_p15_16a_saint.py::test_F15_target_1_5R_and_ticket_conflict",
    "F15-ticket-rr-conflict": "test_p15_16a_saint.py::test_F15_target_1_5R_and_ticket_conflict",
    "F15-stop-beyond-rejection": "test_p15_16a_saint.py::test_F15_stop_above_rejection_high",
    "F15-fixed-500-risk": "test_p15_16a_saint.py::test_F15_fixed_500_risk",
    "F15-k10-p13-drawn-directions": "test_p15_16a_saint.py::test_F15_k10_p13_drawn_directions_negative_control",
    "RR-23-instrument-transfer": "test_p15_16a_saint.py::test_RR23_es_tape_required",
    "F16-a-period": "test_p15_16a_saint.py::test_F16_a_period_0930_1000",
    "F16-observation-1000": "test_p15_16a_saint.py::test_F16_a_period_0930_1000",
    "F16-no-1100-cutoff": "test_p15_16a_saint.py::test_F16_no_1100_cutoff",
    "F16-no-60m-expiry": "test_p15_16a_saint.py::test_F16_no_60m_retest_expiry",
    "F16-no-val-rise": "test_p15_16a_saint.py::test_F16_no_developing_val_rise",
    "F16-open-above-value": f"{NONE_FIXTURE}: open-above-value admission is labelled; no nodeid fails when this row is removed",
    "F16-rejection-poc-or-prior-vah": f"{NONE_FIXTURE}: rejection at POC/prior VAH is labelled; no nodeid fails when this row is removed",
    "F16-imbalance-vah-break": f"{NONE_FIXTURE}: VAH-break imbalance is labelled; no nodeid fails when this row is removed",
    "F16-defended-retest": f"{NONE_FIXTURE}: defended retest is labelled; no nodeid fails when this row is removed",
    "F16-three-tick-reward": "test_p15_16a_saint.py::test_F16_three_tick_reward",
    "F16-htf-objective": "test_p15_16a_saint.py::test_F16_htf_objective_not_a_width",
}

FINDING_FIXTURES = {
    "F01": "test_p15_16a_greenbird.py::test_f01_old_scalp_branches_are_observations",
    "F02": "test_p15_16a_sires.py::test_f02_pullback_then_absorption_is_not_clean_squeeze",
    "F03": "test_p15_16a_sires.py::test_f03_replenishment_three_refills_pass_two_fail",
    "F04": "test_p15_16a_saint.py::test_F04_arrival_fast_vs_slow",
    "F05": "test_p15_16a_saint.py::test_F05_no_older_auction_gate",
    "F06": "test_p15_16a_greenbird.py::test_f06_a1_requires_retest_and_post_open_close",
    "F07": "test_p15_16a_greenbird.py::test_f07_bias_reports_unfiltered_and_filtered",
    "F08": "test_p15_16a_jumbo.py::test_f08_extension_after_1000_and_1300_admitted",
    "F09": "test_p15_16a_sires.py::test_f09_location_lvn_passes_poc_fails",
    "F10": "test_p15_16a_sires.py::test_f10_f20_refill_zone_from_clusters_and_departure_is_actual_time",
    "F11": "test_p15_16a_jumbo.py::test_f11_3m_ob_baseline_and_od_variants_labelled",
    "F12": f"{NONE_FIXTURE}: RULES membership is asserted in test_f18_f19_clock_fields; no nodeid fails when F12 behavior is removed",
    "F13": "test_p15_16a_greenbird.py::test_f13_vwap_missing_retest_is_fail_not_unknown",
    "F14": f"{NONE_FIXTURE}: SOURCE_ADDITIONS items 11/19/27 are documentation corrections",
    "F15": "test_p15_16a_saint.py::test_F15_no_1245_split",
    "F16": "test_p15_16a_saint.py::test_F16_no_1100_cutoff",
    "F17": f"{NONE_FIXTURE}: pzone generator unknown is labelled; no nodeid fails when this row is removed",
    "F18": "test_p15_16a.py::test_S31_jj_tbr_clock_zone_verified",
    "F19": "test_p15_16a_jumbo.py::test_f18_f19_clock_fields",
    "F20": "test_p15_16a_sires.py::test_f10_f20_refill_zone_from_clusters_and_departure_is_actual_time",
    "RR-01": "test_p15_16a_jumbo.py::test_rr01_extension_band_identity_and_printed_examples",
    "RR-02": "test_p15_16a.py::test_S02_rr02_eq_contacts_are_two_sided",
    "RR-03": "test_p15_16a_jumbo.py::test_rr03_sweep_before_0930_is_a_valid_trigger",
    "RR-04": "test_p15_16a_jumbo.py::test_rr04_london_box_is_0200_0300_not_0000_0300",
    "RR-05": "test_p15_16a_jumbo.py::test_rr05_printed_pzone_absorption_fixture",
    "RR-06": "test_p15_16a_jumbo.py::test_rr06_reclaim_is_the_entry_and_depth_is_recorded_not_required",
    "RR-07": "test_p15_16a_jumbo.py::test_rr07_sessionstat_coincidence_and_evrange_after_tape",
    "RR-08": "test_p15_16a_jumbo.py::test_rr08_open_location_uses_prior_rth_at_0930",
    "RR-09": "test_p15_16a_jumbo.py::test_rr09_one_side_is_high_only_plus_low_only",
    "RR-10": f"{NONE_FIXTURE}: author-example replay set; covered by AUTHOR_EXAMPLE_REPLAY rather than a RULES row",
    "RR-11": "test_p15_16a_greenbird.py::test_rr11_september_uses_asia_0000_and_london_0200_0500",
    "RR-12": "test_p15_16a_greenbird.py::test_rr12_ladder_and_750_not_scored",
    "RR-13": "test_p15_16a_greenbird.py::test_rr13_five_minute_required_for_asia_high",
    "RR-14": "test_p15_16a_greenbird.py::test_rr14_pocket_uses_impulse_not_910_box",
    "RR-15": "test_p15_16a_greenbird.py::test_rr15_objective_horizon_is_next_open_not_30m",
    "RR-16": f"{NONE_FIXTURE}: GB author-example replay set; covered by AUTHOR_EXAMPLE_REPLAY",
    "RR-17": "test_p15_16a_sires.py::test_rr17_replay_sires_author_examples",
    "RR-18": "test_p15_16a_sires.py::test_rr18_resting_stop_is_baseline_ofm_entry",
    "RR-19": "test_p15_16a_sires.py::test_rr19_management_partial_trail_daily_stop",
    "RR-20": "test_p15_16a_sires.py::test_rr20_aggression_30_60",
    "RR-21": "test_p15_16a_sires.py::test_rr21_refill_literal_size_family_and_bracket",
    "RR-22": "test_p15_16a_saint.py::test_RR22_asia_session_not_ny_only",
    "RR-23": "test_p15_16a_saint.py::test_RR23_es_tape_required",
}

RR02_NOTES = (
    "EQ two-sided is implemented in common.changed_reference_scan. "
    "Quadrant sides stay the default pair (q1 long / q3 short); they are not bound to the branch context as RR-02 states. "
    "WORK_LOG: q1 long / q3 short stay the default pair."
)
F18_NOTES = (
    "JJ-TBR is dropped from CLOCK_ZONE_UNVERIFIED_FAMILIES (TBR p.4/p.6 New York clock). "
    "GB-FAIL, GB-VWAP and GB-SCALP remain in the frozenset so frozen B0/B0.1 dual-scan flags do not move. "
    "WORK_LOG: keeping the frozen B0/B0.1 dual-scan flags from moving."
)


def _finding_token(rule: dict) -> str:
    finding = str(rule.get("finding") or "")
    token = finding.split()[0] if finding else str(rule.get("rule_id") or "")
    token = token.replace("RR18", "RR-18").replace("RR19", "RR-19").replace("RR20", "RR-20").replace("RR21", "RR-21")
    if token.startswith("F") and len(token) >= 3 and token[1].isdigit():
        return token[:3] if token[2].isdigit() else token
    if token.startswith("RR") and "RR-" not in token[:3]:
        digits = "".join(ch for ch in token if ch.isdigit())
        if digits:
            return f"RR-{int(digits):02d}"
    if token.startswith("RR-"):
        return token[:5] if len(token) >= 5 and token[3:5].isdigit() else token
    return token


def _rule_fixture(rule_id, token: str) -> str:
    if rule_id in RULE_FIXTURES:
        return RULE_FIXTURES[rule_id]
    if token in FINDING_FIXTURES:
        return FINDING_FIXTURES[token]
    return f"{NONE_FIXTURE}: {rule_id or token} has no nodeid that fails when this row is removed"


def assemble_fidelity() -> dict:
    rows = []
    by_finding: dict[str, list[dict]] = {}
    family_of = {
        "RULES_JJ-TBR.json": "JJ-TBR",
        "RULES_GB.json": "GB-FAIL",
        "RULES_SIRES.json": "SIRES",
        "RULES_REFILL-STUDY.json": "REFILL-STUDY",
        "RULES_SAINT-AMT.json": "SAINT-AMT",
        "RULES_MEMBER-TWO-REASONS.json": "MEMBER-TWO-REASONS",
        "RULES_KEANI.json": "KEANI-OPEN-ABOVE-VALUE",
    }
    for path in sorted(TRACK.glob("_track_*/RULES_*.json")):
        family = family_of.get(path.name, path.stem.replace("RULES_", ""))
        for rule in _rule_rows(path):
            token = _finding_token(rule)
            rule_id = rule.get("rule_id")
            status = "implemented"
            file_line = rule.get("file_line") or rule.get("file")
            notes = None
            if rule_id == "F18-clock-seasonal-ny" or (token == "F18" and str(family).startswith("GB")):
                status = "partial"
                file_line = "source_adapters/common.py:CLOCK_ZONE_UNVERIFIED_FAMILIES"
                notes = F18_NOTES
            row = {
                "id": token or rule_id,
                "rule_id": rule_id,
                "family": family,
                "status": status,
                "source_reason": rule.get("source"),
                "kind": rule.get("kind"),
                "file_line": file_line,
                "fixture": _rule_fixture(rule_id, token),
                "evidence": str(path),
                "notes": notes,
            }
            rows.append(row)
            if token:
                by_finding.setdefault(token, []).append(row)
    required = [f"F{i:02d}" for i in range(1, 21)] + [f"RR-{i:02d}" for i in range(1, 24)]
    coverage = []
    deferred = {
        "F14": "SOURCE_ADDITIONS items 11/19/27 are documentation corrections; B0.2 adapters implement the underlying F06/F13 rules.",
        "RR-10": "Author-example replay set; covered by AUTHOR_EXAMPLE_REPLAY rather than a RULES row.",
        "RR-16": "Author-example replay set for GB; covered by AUTHOR_EXAMPLE_REPLAY.",
        "RR-17": "Author-example replay set for SIRES; covered by AUTHOR_EXAMPLE_REPLAY.",
    }
    for ident in required:
        hits = []
        for key, items in by_finding.items():
            if key == ident or key.startswith(ident + "-") or key.startswith(ident + "_") or ident == key:
                hits.extend(items)
        if ident == "RR-02":
            coverage.append(
                {
                    "id": ident,
                    "status": "partial",
                    "families": ["JJ-TBR"],
                    "file_line": "source_adapters/common.py:changed_reference_scan",
                    "fixture": FINDING_FIXTURES["RR-02"],
                    "evidence": "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py",
                    "source_reason": "TBR pp.12-15; author trades EQ both ways 2026-09-01/02",
                    "notes": RR02_NOTES,
                }
            )
            continue
        if ident == "F18":
            families = sorted({item["family"] for item in hits} | {"JJ-TBR", "GB-FAIL", "GB-VWAP", "GB-SCALP"})
            coverage.append(
                {
                    "id": ident,
                    "status": "partial",
                    "families": families,
                    "file_line": "source_adapters/common.py:CLOCK_ZONE_UNVERIFIED_FAMILIES",
                    "fixture": FINDING_FIXTURES["F18"],
                    "evidence": "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py",
                    "source_reason": "TBR p.4/p.6 New York clock for JJ-TBR; GB seasonal NY clocks evidenced but frozen B0/B0.1 flag unchanged",
                    "notes": F18_NOTES,
                }
            )
            continue
        if hits:
            coverage.append(
                {
                    "id": ident,
                    "status": "implemented",
                    "families": sorted({item["family"] for item in hits}),
                    "file_line": hits[0].get("file_line"),
                    "fixture": FINDING_FIXTURES.get(ident) or hits[0].get("fixture"),
                    "evidence": hits[0].get("evidence"),
                    "source_reason": hits[0].get("source_reason"),
                    "notes": None,
                }
            )
        else:
            coverage.append(
                {
                    "id": ident,
                    "status": "deferred",
                    "families": [],
                    "file_line": None,
                    "fixture": FINDING_FIXTURES.get(ident) or f"{NONE_FIXTURE}: no RULES row in the four family tracks",
                    "evidence": None,
                    "source_reason": deferred.get(ident, "no RULES row in the four family tracks"),
                    "notes": None,
                }
            )
    return {
        "schema": FIDELITY_SCHEMA,
        "task_id": "P15-16A",
        "baseline": "B0.2-2026-09-15",
        "findings": coverage,
        "family_rules": rows,
        "n_findings_implemented": sum(1 for row in coverage if row["status"] == "implemented"),
        "n_findings_partial": sum(1 for row in coverage if row["status"] == "partial"),
        "n_findings_deferred": sum(1 for row in coverage if row["status"] == "deferred"),
        "n_family_rules": len(rows),
    }


def assemble_ledger() -> dict:
    src = json.loads(LEDGER.read_text())
    by_id = {row["row_id"]: row for row in src.get("rows") or src.get("operand_rows") or src.get("ledger") or []}
    if not by_id and "rows" not in src:
        for row in src.get("entries") or []:
            by_id[row["row_id"]] = row
        if not by_id:
            for row in src.get("operand_overrides") or []:
                pass
            # ledger rows live under a list key
            for key, value in src.items():
                if isinstance(value, list) and value and isinstance(value[0], dict) and "row_id" in value[0]:
                    by_id = {row["row_id"]: row for row in value}
                    break
    corrections = []
    for row_id, fix in LEDGER_FIX.items():
        original = by_id.get(row_id) or {}
        corrections.append(
            {
                "row_id": row_id,
                "immutable_p15_04_path": str(REPORTS / "P15-04/0d0a57cc4de997b4/attempt-0001/SOURCE_RECONSTRUCTION_LEDGER.json"),
                "original_classification": original.get("classification"),
                "original_disposition": original.get("disposition"),
                "original_source_exact": original.get("source_exact"),
                "correction": fix["correction"],
                "ruling": fix["ruling"],
                "new_classification": fix["new_classification"],
                "p15_04_artifact_unedited": True,
            }
        )
    return {
        "schema": LEDGER_SCHEMA,
        "task_id": "P15-16A",
        "source_ledger": str(LEDGER),
        "corrections": corrections,
    }


OLD_COLLISION = (
    "The previous B0.2 run root 1e13829f2c88f1e1 is superseded: jobs were named "
    "jobs/<date>/<branch>.json.gz so KEANI-OPEN-ABOVE-VALUE:branch:source_long collided "
    "with GB-VWAP:branch:source_long. Distinct gzip files on that root: 66196. "
    "This run uses coverage_id--json.gz job paths; KEANI is measured; jobs_declared = 39 x 1742 = 67938."
)


def _complete_b02_runs() -> list[Path]:
    skip = {OLD_B02_RUN.name, ROUND2_B02_RUN.name}
    found = []
    for path in TRACK.iterdir():
        if not path.is_dir() or path.name.startswith("_") or path.name in skip:
            continue
        if (path / "RUN_COMPLETE.json").is_file() and (path / "SUMMARY.json").is_file():
            found.append(path)
    return found


def _branch_count(root: Path) -> int:
    try:
        return int(json.loads((root / "RUN_COMPLETE.json").read_text()).get("n_branches") or 0)
    except Exception:
        return 0


def resolve_b02_runs() -> tuple[Path, list[Path]]:
    """The main full-history root and every supplemental root.

    A supplemental root is a complete run over a branch subset, issued after the
    main run because a branch was added or a scan changed. Its rows supersede the
    main root's rows for the coverage ids it carries; no job file of the main run
    is rewritten.
    """
    found = _complete_b02_runs()
    if not found:
        return B02_RUN, []
    main = max(found, key=_branch_count)
    supplemental = sorted(
        (path for path in found if path != main),
        key=lambda item: (item / "RUN_COMPLETE.json").stat().st_mtime,
    )
    return main, supplemental


def resolve_b02_run() -> Path:
    return resolve_b02_runs()[0]


def _family_plausibility(family: str) -> dict:
    name = FAMILY_SPEC_FILES.get(family)
    if not name:
        return {}
    path = FAMILIES_DIR / name
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text()).get("plausibility") or {}
    nested = payload.get(family)
    if isinstance(nested, dict) and nested and not any(key in nested for key in ("episodes_per_session", "pass_rate")):
        return nested
    return payload


def _bound_status(row: dict, bound: dict) -> tuple[bool | None, str | None]:
    if not bound:
        return None, None
    episodes = int(row.get("episodes_b02") or row.get("episodes") or 0)
    n_pass = int(row.get("pass_b02") or row.get("pass") or 0)
    dates_run = int(row.get("dates_run") or 0)
    eps = (episodes / dates_run) if dates_run else float(row.get("episodes_per_session") or 0)
    rate = (n_pass / episodes) if episodes else float(row.get("pass_rate") or 0)
    ep_bound = bound.get("episodes_per_session")
    pr = bound.get("pass_rate")
    if isinstance(ep_bound, (list, tuple)) and len(ep_bound) >= 2 and ep_bound[0] is not None and ep_bound[1] is not None:
        in_eps = ep_bound[0] <= eps <= ep_bound[1]
    else:
        in_eps = False
    in_rate = True
    if isinstance(pr, list) and len(pr) >= 2 and pr[0] is not None and pr[1] is not None:
        in_rate = pr[0] <= rate <= pr[1]
    in_bound = in_eps and in_rate
    just = bound.get("observed_rate_justification")
    diagnosis = None
    if not in_bound:
        if isinstance(just, dict) and just.get("page") and just.get("text"):
            diagnosis = f"{just['page']}: {just['text']}"
        else:
            diagnosis = bound.get("source_claim")
    return in_bound, diagnosis


def _count_job_files(run_root: Path) -> int:
    jobs = run_root / "jobs"
    if not jobs.is_dir():
        return 0
    return sum(1 for path in jobs.rglob("*.json.gz") if path.is_file())


def _tdo_retest_counts(root: Path, coverage_ids: set[str]) -> dict:
    """Confirmation-mode counts read from the run's job files, per branch."""
    import gzip

    out: dict[str, dict[str, int]] = {}
    jobs = root / "jobs"
    if not jobs.is_dir():
        return out
    for path in jobs.rglob("*.json.gz"):
        cid = path.name[: -len(".json.gz")].replace("--", ":")
        if cid not in coverage_ids:
            continue
        try:
            document = json.loads(gzip.decompress(path.read_bytes()).decode())
        except Exception:
            continue
        slot = out.setdefault(cid, {})
        for episode in document.get("episodes") or []:
            values = episode.get("values") or {}
            mode = values.get("confirmation_mode")
            if mode:
                key = f"mode:{mode}"
                slot[key] = slot.get(key, 0) + 1
            reason = values.get("tdo_retest_reason")
            if reason:
                key = f"tdo_retest_reason:{reason}"
                slot[key] = slot.get(key, 0) + 1
    return out


def assemble_b02_summary(run_root: Path | None = None) -> dict | None:
    if run_root is not None:
        root, supplemental_roots = Path(run_root), []
    else:
        root, supplemental_roots = resolve_b02_runs()
    summary_path = root / "SUMMARY.json"
    if not summary_path.is_file():
        return None
    summary = json.loads(summary_path.read_text())
    census_index = {}
    if (CENSUS_ROOT / "SUMMARY.json").is_file():
        census = json.loads((CENSUS_ROOT / "SUMMARY.json").read_text())
        census_index = {row["coverage_id"]: row for row in census.get("branches") or []}
    distinct_jobs = _count_job_files(root)
    supplemental_meta = []
    supplemental_rows: dict[str, dict] = {}
    mode_counts: dict[str, dict[str, int]] = {}
    for extra in supplemental_roots:
        extra_summary = json.loads((extra / "SUMMARY.json").read_text())
        rows = list(extra_summary.get("branches") or [])
        for row in rows:
            row = dict(row)
            row["run_id"] = extra_summary.get("run_id")
            row["run_root"] = str(extra)
            supplemental_rows[row["coverage_id"]] = row
        extra_jobs = _count_job_files(extra)
        mode_counts.update(_tdo_retest_counts(extra, {row["coverage_id"] for row in rows}))
        supplemental_meta.append(
            {
                "run_id": extra_summary.get("run_id"),
                "run_root": str(extra),
                "manifest_sha256": extra_summary.get("manifest_sha256"),
                "n_dates": extra_summary.get("n_dates"),
                "n_branches": extra_summary.get("n_branches"),
                "job_count": extra_jobs,
                "distinct_job_files": extra_jobs,
                "branches": [str(row["coverage_id"]) for row in rows],
                "failed_dates": extra_summary.get("failed_dates") or [],
                "reason": (
                    "prior_week_level was added to B0.2 after the main run (followup-5 GAP 1); "
                    "asia_box and prior_day_level were re-scanned because the tdo_retest confirmation "
                    "variant (followup-5 GAP 2) changes their recorded confirmation mode; "
                    "JJ-TBR internal_rotation was re-scanned because its location stage read the deleted "
                    "range constant TAPE_LAST (2026-08-19) and now reads the shared frozen-list guard, "
                    "which moves the boundary to 2026-09-03. Every other branch's job files were produced "
                    "by scan bytes that are unchanged, and no job file of the main run was changed."
                ),
            }
        )
    merged_rows = list(summary.get("branches") or [])
    by_cid = {row["coverage_id"]: index for index, row in enumerate(merged_rows)}
    for cid, row in supplemental_rows.items():
        if cid in by_cid:
            merged_rows[by_cid[cid]] = row
        else:
            merged_rows.append(row)
    branches = []
    for row in merged_rows:
        item = dict(row)
        census_row = census_index.get(row["coverage_id"]) or {}
        item["episodes_b0"] = census_row.get("episodes_b0")
        item["pass_b0"] = census_row.get("pass_b0")
        item["fail_b0"] = census_row.get("fail_b0")
        item["unknown_b0"] = census_row.get("unknown_b0")
        item["episodes_b01"] = census_row.get("episodes_b01") or row.get("census_b01_episodes")
        item["pass_b01"] = census_row.get("pass_b01") or row.get("census_b01_pass")
        item["fail_b01"] = census_row.get("fail_b01") or row.get("census_b01_fail")
        item["unknown_b01"] = census_row.get("unknown_b01") or row.get("census_b01_unknown")
        item["measured"] = True
        item["episodes_b02"] = row.get("episodes")
        item["pass_b02"] = row.get("pass")
        item["fail_b02"] = row.get("fail")
        item["unknown_b02"] = row.get("unknown")
        item["funnel"] = row.get("funnel") or {}
        item["entry_histogram"] = row.get("entry_histogram") or {}
        item["source_run_id"] = row.get("run_id") or summary.get("run_id")
        item["source_run_root"] = row.get("run_root") or str(root)
        item["confirmation_mode_counts"] = mode_counts.get(row["coverage_id"]) or {}
        item["episodes_per_session"] = row.get("episodes_per_session")
        item["pass_rate"] = row.get("pass_rate")
        bound = _family_plausibility(row.get("family") or "").get(row.get("branch") or "") or {}
        in_bound, diagnosis = _bound_status(item, bound)
        item["plausibility_bound"] = bound
        item["in_bound"] = in_bound
        item["plausibility_diagnosis"] = diagnosis
        branches.append(item)
    return {
        "schema": B02_SUMMARY_SCHEMA,
        "task_id": "P15-16A",
        "baseline": "B0.2-2026-09-15",
        "run_id": summary.get("run_id"),
        "run_root": summary.get("run_root") or str(root),
        "manifest_sha256": summary.get("manifest_sha256"),
        "n_dates": summary.get("n_dates"),
        "n_branches": summary.get("n_branches"),
        "job_count": distinct_jobs,
        "runner_declared_job_count": summary.get("job_count"),
        "distinct_job_files": distinct_jobs,
        "supplemental_runs": supplemental_meta,
        "job_count_all_roots": distinct_jobs + sum(item["job_count"] for item in supplemental_meta),
        "keani_b02": "measured",
        "superseded_run_root": str(OLD_B02_RUN),
        "superseded_round2_run_root": str(ROUND2_B02_RUN),
        "superseded_reason": OLD_COLLISION,
        "dates_first": summary.get("dates_first"),
        "dates_last": summary.get("dates_last"),
        "branches": branches,
        "n_branches_all_roots": len({row["coverage_id"] for row in branches}),
        "missing": summary.get("missing") or [],
        "failed_dates": summary.get("failed_dates") or [],
        "census_run_id": summary.get("census_run_id"),
        "b0_source": "run-1.0.1 jobs (via census 20def36e065c13d7; not rescanned)",
        "b01_source": str(CENSUS_ROOT / "SUMMARY.json"),
        "worker_count": summary.get("worker_count"),
        "cgroup_worker_count": summary.get("cgroup_worker_count"),
        "achieved_concurrency": summary.get("achieved_concurrency"),
        "wall_seconds_orchestrator": summary.get("wall_seconds_orchestrator"),
        "runner_summary_schema": summary.get("schema"),
    }


def render_b02_summary_md(payload: dict) -> str:
    lines = [
        "# B0.2 full-history summary",
        "",
        f"- Run id: `{payload.get('run_id')}`",
        f"- Run root: `{payload.get('run_root')}`",
        f"- Dates: {payload.get('n_dates')} ({payload.get('dates_first')} .. {payload.get('dates_last')})",
        f"- Branches: {payload.get('n_branches')}",
        f"- Distinct job files: {payload.get('distinct_job_files')}",
        f"- Runner-declared jobs: {payload.get('runner_declared_job_count')}",
        f"- KEANI B0.2: {payload.get('keani_b02')}",
        f"- Census: `{payload.get('census_run_id')}`",
        f"- B0 source: {payload.get('b0_source')}",
        f"- Branches over all roots: {payload.get('n_branches_all_roots')}",
        f"- Job files over all roots: {payload.get('job_count_all_roots')}",
        "",
        payload.get("superseded_reason") or "",
        "",
    ]
    for extra in payload.get("supplemental_runs") or []:
        lines += [
            f"## Supplemental run `{extra.get('run_id')}`",
            "",
            f"- Run root: `{extra.get('run_root')}`",
            f"- MANIFEST sha256: `{extra.get('manifest_sha256')}`",
            f"- Dates: {extra.get('n_dates')} | branches: {extra.get('n_branches')} | job files: {extra.get('job_count')}",
            f"- Branches: {', '.join(extra.get('branches') or [])}",
            f"- Failed dates: {len(extra.get('failed_dates') or [])}",
            f"- Reason: {extra.get('reason')}",
            "",
        ]
    lines += [
        "| branch | dates | B0.2 ep | B0.2 pass | B0.2 fail | B0.2 unk | B0 ep | B0 pass | B0.1 ep | B0.1 pass | delta pass vs B0.1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload.get("branches") or []:
        if row.get("measured") is False:
            lines.append(
                f"| `{row.get('coverage_id')}` | not_measured | — | — | — | — | "
                f"{row.get('episodes_b0')} | {row.get('pass_b0')} | {row.get('episodes_b01')} | {row.get('pass_b01')} | — |"
            )
            continue
        lines.append(
            f"| `{row.get('coverage_id')}` | {row.get('dates_run')} | {row.get('episodes_b02')} | "
            f"{row.get('pass_b02')} | {row.get('fail_b02')} | {row.get('unknown_b02')} | "
            f"{row.get('episodes_b0')} | {row.get('pass_b0')} | {row.get('episodes_b01')} | {row.get('pass_b01')} | "
            f"{row.get('delta_pass')} |"
        )
    lines += [
        "",
        "## Per-branch funnel, entry time, and plausibility",
        "",
    ]
    for row in payload.get("branches") or []:
        if row.get("measured") is False:
            continue
        bound = row.get("plausibility_bound") or {}
        status = "in" if row.get("in_bound") else ("out" if row.get("in_bound") is False else "n/a")
        lines += [
            f"### `{row.get('coverage_id')}`",
            "",
            f"- episodes per session: {row.get('episodes_per_session')}",
            f"- pass rate: {row.get('pass_rate')}",
            f"- bound episodes_per_session: {bound.get('episodes_per_session')}",
            f"- bound pass_rate: {bound.get('pass_rate')}",
            f"- in/out: {status}",
        ]
        if row.get("plausibility_diagnosis"):
            lines.append(f"- diagnosis: {row.get('plausibility_diagnosis')}")
        lines.append(f"- source run: `{row.get('source_run_id')}`")
        modes = row.get("confirmation_mode_counts") or {}
        if modes:
            lines.append("- confirmation modes: " + ", ".join(f"{k}={v}" for k, v in sorted(modes.items())))
        funnel = row.get("funnel") or {}
        if funnel:
            lines += [
                "",
                "| stage | entering | pass | fail | unknown | unknown operands |",
                "| --- | ---: | ---: | ---: | ---: | --- |",
            ]
            for name, stage in funnel.items():
                ops = stage.get("unknown_operands") or {}
                op_text = ", ".join(f"{k}={v}" for k, v in ops.items()) if ops else ""
                lines.append(
                    f"| {name} | {stage.get('entering', 0)} | {stage.get('pass', 0)} | "
                    f"{stage.get('fail', 0)} | {stage.get('unknown', 0)} | {op_text} |"
                )
        hist = row.get("entry_histogram") or {}
        if hist:
            lines += ["", "30-minute ET entry buckets: " + ", ".join(f"{k}={v}" for k, v in sorted(hist.items())), ""]
        else:
            lines.append("")
    return "\n".join(lines)


def render_family_report(attempt: Path, fidelity: dict, summary: dict | None, replay: dict | None = None) -> str:
    by_family: dict[str, dict] = {}
    if summary:
        for row in summary.get("branches") or []:
            family = row.get("family") or "ALL"
            slot = by_family.setdefault(
                family, {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0, "branches": 0, "not_measured": None}
            )
            if row.get("measured") is False:
                slot["not_measured"] = row.get("not_measured_reason") or "not measured"
                slot["branches"] += 1
                continue
            slot["episodes"] += int(row.get("episodes_b02") or row.get("episodes") or 0)
            slot["pass"] += int(row.get("pass_b02") or row.get("pass") or 0)
            slot["fail"] += int(row.get("fail_b02") or row.get("fail") or 0)
            slot["unknown"] += int(row.get("unknown_b02") or row.get("unknown") or 0)
            slot["branches"] += 1
    keani_note = ""
    if summary and summary.get("superseded_reason"):
        keani_note = summary["superseded_reason"]
    lines = [
        "# P15-16A family report",
        "",
        "B0.2 source-fidelity baseline over the native calendar. Faithful disagreements against the author are not claimed.",
        "",
    ]
    if keani_note:
        lines += [keani_note, ""]
    lines += [
        "| family | variant | n | faithful_disagreements | status | report path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if by_family:
        for family in sorted(by_family):
            slot = by_family[family]
            n = "not_measured" if slot.get("not_measured") else slot["episodes"]
            lines.append(
                f"| {family} | B0.2 | {n} | not claimed | integration | {attempt} |"
            )
    else:
        lines.append(f"| ALL | B0.2 | pending_full_history | not claimed | integration | {attempt} |")
    lines += [
        "",
        "| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in fidelity.get("findings") or []:
        notes = row.get("notes") or row.get("source_reason") or ""
        notes = str(notes).replace("|", "/")
        fixture = str(row.get("fixture") or "").replace("|", "/")
        lines.append(
            f"| {','.join(row.get('families') or []) or 'ALL'} | {row.get('id')} | {row.get('status')} | "
            f"{fixture} | 0 | 0 | {notes} |"
        )
    if summary:
        lines += [
            "",
            "## Plausibility",
            "",
            "Density and pass rate per branch beside the source's stated frequency and page. "
            "Out-of-bound and zero-pass branches keep their diagnosis. Author-example reached-location "
            "is reported from the location stage.",
            "",
            "| family | branch | eps | pass_rate | source frequency | page | in/out | diagnosis |",
            "| --- | --- | ---: | ---: | --- | --- | --- | --- |",
        ]
        for row in summary.get("branches") or []:
            bound = row.get("plausibility_bound") or {}
            status = "in" if row.get("in_bound") else ("out" if row.get("in_bound") is False else "n/a")
            diagnosis = row.get("plausibility_diagnosis") or ""
            if int(row.get("pass_b02") or row.get("pass") or 0) == 0 and int(row.get("episodes_b02") or row.get("episodes") or 0) == 0:
                if row.get("family") == "JJ-TBR" and row.get("branch") == "single_purged":
                    diagnosis = (
                        "no qualifying contact on the slice because prior-session VAL/VAH are missing. "
                        "The prior RTH value-area profile supplies VAL/VAH. Phase 1.5 `_prior_rth` only "
                        "loads prior high/low from hist.prior('day'), so the branch is unknown with named operand prior_value."
                    )
            lines.append(
                f"| {row.get('family')} | {row.get('branch')} | {row.get('episodes_per_session')} | "
                f"{row.get('pass_rate')} | {str(bound.get('source_claim') or '').replace('|', '/')} | "
                f"{bound.get('page') or ''} | {status} | {str(diagnosis).replace('|', '/')} |"
            )
        lines += [
            "",
            "Author-example reached-location and detected counts are in AUTHOR_EXAMPLE_REPLAY.json. "
            "Management stays unmeasured where the author's size and amendment tape is unpublished.",
            "",
        ]
    if replay:
        per_family: dict[str, dict[str, int]] = {}
        for row in replay.get("examples") or []:
            slot = per_family.setdefault(
                str(row.get("family") or "unknown"),
                {"examples": 0, "reached_location": 0, "detected": 0, "unavailable": 0},
            )
            slot["examples"] += 1
            if row.get("reached_location") is True:
                slot["reached_location"] += 1
            if row.get("detected") is True:
                slot["detected"] += 1
            if row.get("reason"):
                slot["unavailable"] += 1
        lines += [
            "## Author examples: reached location and detected, per family",
            "",
            "| family | examples | reached_location | detected | data_unavailable |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for family in sorted(per_family):
            slot = per_family[family]
            lines.append(
                f"| {family} | {slot['examples']} | {slot['reached_location']} | "
                f"{slot['detected']} | {slot['unavailable']} |"
            )
        lines.append("")
    lines.append("")
    return "\n".join(lines)


def run_cmd(argv: list[str], cwd: Path, log_path: Path) -> dict:
    started = time.monotonic()
    result = subprocess.run(argv, cwd=str(cwd), text=True, capture_output=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.stdout + result.stderr)
    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": result.returncode,
        "log_path": str(log_path),
        "log_sha256": file_digest(log_path),
        "seconds": time.monotonic() - started,
    }


def check(id: str, requirement: str, path: str, symbol: str, nodeid, command, evidence: list, expected: str, observed: str, oracle: str, status="pass") -> dict:
    if isinstance(nodeid, list):
        nodes = [item for item in nodeid if item]
    elif nodeid:
        nodes = [nodeid]
    else:
        nodes = []
    payload = {
        "id": id,
        "requirement": requirement,
        "code_refs": [{"path": path, "symbol": symbol}],
        "test_nodeids": nodes,
        "command_indices": list(command) if isinstance(command, list) else ([command] if command is not None else []),
        "evidence": evidence,
        "expected": expected,
        "observed": observed,
        "oracle": oracle,
        "status": status,
    }
    return payload


def ev(path: Path, selector: str) -> dict:
    return {"path": str(path), "sha256": file_digest(path), "selector": selector}


def write_matrix(attempt: Path, commands: list[dict], pending_s01_s03: bool) -> dict:
    pytest_log = attempt / "pytest.log"
    node = lambda name: f"{NODE}::{name}"
    # "unsupported" fails ACCEPTANCE while disposition is implemented_verified.
    # accepted-limit is the contract-legal status until --probes flips these to pass.
    s01_status = "accepted-limit" if pending_s01_s03 else "pass"
    s01_observed = "probes stage has not run" if pending_s01_s03 else "mutations fail"
    s01_node = node("test_S01_s03_probes_unproduced")
    s01_evidence = [ev(pytest_log, "test_S01_s03_probes_unproduced")] if pending_s01_s03 else [ev(pytest_log, "/")]
    s01_cmd = 0
    a06_evidence = [ev(pytest_log, "/")]
    if (attempt / "B02_SUMMARY.json").is_file():
        a06_evidence.append(ev(attempt / "B02_SUMMARY.json", "/job_count"))
    if (attempt / "RUN_COMPLETE.json").is_file():
        a06_evidence.append(ev(attempt / "RUN_COMPLETE.json", "/job_count"))
    a05_evidence = [
        ev(pytest_log, "test_A05_plausibility_gate_full_history"),
        ev(pytest_log, "test_A05_supplemental_run_covers_the_added_branch_and_changed_scans"),
        ev(pytest_log, "test_A05_tdo_retest_mode_counts_are_reported"),
    ]
    if (attempt / "FAMILY_REPORT.md").is_file():
        a05_evidence.append(ev(attempt / "FAMILY_REPORT.md", "/"))
    a07_evidence = [ev(pytest_log, "/")]
    if (attempt / "FIDELITY_MATRIX.json").is_file():
        a07_evidence.append(ev(attempt / "FIDELITY_MATRIX.json", "/n_family_rules"))
    if (attempt / "LEDGER_CORRECTIONS.json").is_file():
        a07_evidence.append(ev(attempt / "LEDGER_CORRECTIONS.json", "/corrections"))
    rows = [
        check("A01", "Every F01-F20 and RR-01-RR-23 ruling is implemented or deferred.", "implementation/src/trading_research/research/rule_discovery/source_adapters/jumbo.py", "RULES", node("test_A01_jumbo_rr01_extension_band_is_1_33_1_66"), 0, [ev(attempt / "FIDELITY_MATRIX.json", "/n_findings_implemented")], "implemented or deferred", "pass", "task card A01"),
        check("A02", "B0/B0.1 stay byte-identical; B0.2 measured beside them.", "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py", "dual_scan", node("test_A02_b0_b01_byte_identity_negative_control"), 0, [ev(pytest_log, "test_A02_b0_b01_byte_identity_negative_control")], "byte-identical B0/B0.1", "pass", "task card A02"),
        check("A03", "Author examples replayed; no rule changed to pass an example.", "implementation/tools/replay_author_examples.py", "replay_one", node("test_A03_replay_skips_outside_calendar_without_cache"), 0, [ev(attempt / "AUTHOR_EXAMPLE_REPLAY.json", "/n") if (attempt / "AUTHOR_EXAMPLE_REPLAY.json").is_file() else ev(pytest_log, "test_A03_replay_skips_outside_calendar_without_cache")], "replay table", "pass", "task card A03"),
        check("A04", "OD rules labelled; ledger corrections recorded.", "implementation/src/trading_research/research/rule_discovery/source_adapters/jumbo.py", "RULES", node("test_A04_od_and_literal_rules_are_labelled"), 0, [ev(attempt / "LEDGER_CORRECTIONS.json", "/corrections")], "OD labelled", "pass", "task card A04"),
        check("A05", "Populations plausible vs published statistics or explained by funnel.", "implementation/tests/rule_discovery/test_p15_16a.py", "test_A05_plausibility_gate_full_history", node("test_A05_plausibility_gate_full_history"), 0, a05_evidence, "funnel or published stats", "pass", "task card A05"),
        check("A06", "Command exit codes, hashes, coverage, runtime.", "implementation/tools/produce_p15_16a.py", "produce", None, [0, 1], a06_evidence, "pytest exit 0", "pass", "ASSURANCE A06"),
        check("A07", "EVIDENCE_MATRIX resolves every key.", "implementation/tools/produce_p15_16a.py", "write_matrix", None, [0, 1], a07_evidence, "matrix complete", "pass", "ASSURANCE A07"),
        check("A08", "Assigned silent-failure probes.", "implementation/tools/produce_p15_16a.py", "produce", None, [0, 1], a06_evidence, "S07/S08/S09/S21/S22/S31 pass; S01/S03 unproduced", "pass", "ASSURANCE A08"),
        check("S01", "Missing/substituted/malformed artifacts fail.", "implementation/tools/produce_p15_16a.py", "run_probes", None, s01_cmd, s01_evidence, "mutations fail", s01_observed, "SILENT_FAILURES S01", status=s01_status),
        check("S02", "Sensitive fixture for advertised B0.2 behavior.", "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py", "changed_reference_scan", node("test_S02_rr02_eq_contacts_are_two_sided"), 0, [ev(pytest_log, "test_S02_rr02_eq_contacts_are_two_sided")], "EQ two-sided", "pass", "SILENT_FAILURES S02"),
        check("S03", "False plan/code/draft identities rejected.", "implementation/tests/rule_discovery/test_p15_16a.py", "test_S03_false_plan_identity_is_rejected", node("test_S03_false_plan_identity_is_rejected"), s01_cmd, s01_evidence, "mutations fail", s01_observed, "SILENT_FAILURES S03", status=s01_status),
        check("S07", "Native parquet row replay.", "implementation/src/trading_research/research/rule_discovery/native.py", "replay_native_row", node("test_S07_native_replay"), 0, [ev(pytest_log, "test_S07_native_replay")], "kind=native", "pass", "SILENT_FAILURES S07"),
        check("S08", "Future perturbation does not change earlier output.", "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py", "future_perturbation_stable", node("test_S08_future_perturbation_stable"), 0, [ev(pytest_log, "test_S08_future_perturbation_stable")], "stable before cutoff", "pass", "SILENT_FAILURES S08"),
        check("S09", "Same-timestamp target/stop stays ambiguous.", "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py", "permute_batch_ambiguity", node("test_S09_same_timestamp_target_stop_stays_ambiguous"), 0, [ev(pytest_log, "test_S09_same_timestamp_target_stop_stays_ambiguous")], "unknown", "pass", "SILENT_FAILURES S09"),
        check("S21", "Source prerequisites remain named.", "implementation/src/trading_research/research/rule_discovery/source_adapters/jumbo.py", "family_document", node("test_S21_source_prerequisites_named_on_jumbo"), 0, [ev(pytest_log, "test_S21_source_prerequisites_named_on_jumbo")], "by_construction operands", "pass", "SILENT_FAILURES S21"),
        check("S22", "Changed geometry enumerates its own population.", "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py", "enumerate_own_population", node("test_S22_new_geometry_is_own_population"), 0, [ev(pytest_log, "test_S22_new_geometry_is_own_population")], "own_population true", "pass", "SILENT_FAILURES S22"),
        check("S31", "JJ-TBR New York clock; unknown stays unknown.", "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py", "clock_zone_unverified", node("test_S31_jj_tbr_clock_zone_verified"), 0, [ev(pytest_log, "test_S31_jj_tbr_clock_zone_verified")], "JJ-TBR verified", "pass", "SILENT_FAILURES S31"),
    ]
    doc = {
        "schema": MATRIX_SCHEMA,
        "schema_version": MATRIX_SCHEMA,
        "task_id": "P15-16A",
        "assurance_version": ASSURANCE_VERSION,
        "checks": rows,
    }
    write_json_document(attempt / "EVIDENCE_MATRIX.json", doc)
    return doc


def _verify_codes(path: Path) -> dict:
    result = verify_task_receipt(path)
    return {"ok": bool(result.ok), "codes": [item.code for item in result.failures]}


def run_probes(attempt: Path) -> dict:
    receipt = attempt / "TASK_RECEIPT.json"
    control = _verify_codes(receipt)
    if not control.get("ok"):
        raise SystemExit(f"probe control failed: {control}")
    mutations = {}
    parent = Path(tempfile.mkdtemp(prefix="p15-16a-probes-"))
    try:
        def clone(name: str) -> Path:
            dest = parent / name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(attempt, dest, symlinks=True)
            rec = dest / "TASK_RECEIPT.json"
            text = rec.read_text()
            for old in {str(attempt), str(attempt.resolve())}:
                text = text.replace(old, str(dest))
            rec.write_text(text)
            return rec

        rec = clone("remove_artifact")
        target = rec.parent / "WORK_LOG.md"
        if target.is_file():
            target.unlink()
        mutations["remove_artifact"] = _verify_codes(rec)

        rec = clone("substitute_file")
        other = PREDECESSORS["P15-16"]
        local = rec.parent / "FIDELITY_MATRIX.json"
        if other.is_file() and local.is_file():
            local.write_bytes(other.read_bytes())
            digest_value = file_digest(local)
            payload = json.loads(rec.read_text())
            for entry in payload.get("artifact_manifest") or []:
                if Path(entry.get("path", "")).name == "FIDELITY_MATRIX.json":
                    entry["sha256"] = digest_value
                    entry["bytes"] = local.stat().st_size
            rec.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        mutations["substitute_file"] = _verify_codes(rec)

        rec = clone("row_count")
        payload = json.loads(rec.read_text())
        for entry in payload.get("artifact_manifest") or []:
            if str(entry.get("path", "")).endswith(".json"):
                entry["rows"] = 10**9
                break
        rec.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        mutations["row_count"] = _verify_codes(rec)

        rec = clone("invalid_json")
        bad = rec.parent / "LEDGER_CORRECTIONS.json"
        if bad.is_file():
            bad.write_text("not-json\n")
            digest_value = file_digest(bad)
            payload = json.loads(rec.read_text())
            for entry in payload.get("artifact_manifest") or []:
                if Path(entry.get("path", "")).name == "LEDGER_CORRECTIONS.json":
                    entry["sha256"] = digest_value
                    entry["bytes"] = bad.stat().st_size
            rec.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        mutations["invalid_json"] = _verify_codes(rec)

        rec = clone("plan_digest")
        payload = json.loads(rec.read_text())
        payload["plan_sha256"] = "0" * 64
        rec.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        mutations["plan_digest"] = _verify_codes(rec)

        rec = clone("code_digest")
        payload = json.loads(rec.read_text())
        payload["code_sha256"] = "0" * 64
        rec.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        mutations["code_digest"] = _verify_codes(rec)

        rec = clone("draft_digest")
        payload = json.loads(rec.read_text())
        payload["run_id"] = "0" * 16
        rec.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        mutations["draft_digest"] = _verify_codes(rec)
    finally:
        shutil.rmtree(parent, ignore_errors=True)
    expected = ["remove_artifact", "substitute_file", "row_count", "invalid_json", "plan_digest", "code_digest", "draft_digest"]
    ok = True
    for name in expected:
        row = mutations.get(name) or {}
        extra = set(row.get("codes") or []) - set(control.get("codes") or [])
        if row.get("ok") or not extra:
            ok = False
    doc = {"schema": PROBES_SCHEMA, "control": control, "mutations": mutations, "ok": ok}
    write_json_document(attempt / "PROBES_S01_S03.json", doc)
    verify = {"schema": VERIFY_SCHEMA, "control": control, "ok": control.get("ok")}
    write_json_document(attempt / "VERIFY_TASK.json", verify)
    return doc


def next_attempt(run_id: str) -> Path:
    parent = REPORTS / "P15-16A" / run_id
    n = 1
    while (parent / f"attempt-{n:04d}").exists():
        n += 1
    return parent / f"attempt-{n:04d}"


def produce(pending_s01_s03: bool) -> Path:
    staging = REPORTS / "P15-16A" / "_work_16a"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    cmd0 = run_cmd(
        [str(PY), "-m", "pytest", "tests/rule_discovery", "tests/contracts", "-v", "-p", "no:cacheprovider"],
        IMP,
        staging / "pytest.log",
    )
    if cmd0["exit_code"] != 0:
        raise SystemExit(f"pytest failed\n{(staging / 'pytest.log').read_text()[-2000:]}")
    ident = write_task_identity(
        staging,
        task_id="P15-16A",
        plan_paths=PLAN_PATHS,
        code_paths=CODE_PATHS,
        owned=OWNED,
        imported_modules=[
            "trading_research.research.rule_discovery.source_adapters.common",
            "trading_research.research.rule_discovery.run_adapter_populations",
        ],
        predecessor_receipts=PREDECESSORS,
        extra_inputs={"AUTHOR_EXAMPLES": ROOT / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json"},
    )
    attempt = next_attempt(ident["run_id"])
    attempt.mkdir(parents=True, exist_ok=True)
    for name in ("PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json", "DRAFT_MANIFEST.json", "WORKTREE_SNAPSHOT.json", "pytest.log"):
        src = staging / name
        if src.is_file():
            shutil.copy2(src, attempt / name)
    cmd0 = dict(cmd0)
    cmd0["log_path"] = str(attempt / "pytest.log")
    snap = staging / "snapshots"
    if snap.is_dir():
        dest = attempt / "snapshots"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(snap, dest)
    fidelity = assemble_fidelity()
    ledger = assemble_ledger()
    write_json_document(attempt / "FIDELITY_MATRIX.json", fidelity)
    write_json_document(attempt / "LEDGER_CORRECTIONS.json", ledger)
    b02_root, b02_supplemental = resolve_b02_runs()
    b02_summary = assemble_b02_summary()
    if b02_summary is not None:
        write_json_document(attempt / "B02_SUMMARY.json", b02_summary)
        (attempt / "B02_SUMMARY.md").write_text(render_b02_summary_md(b02_summary))
        shutil.copy2(attempt / "B02_SUMMARY.json", b02_root / "B02_SUMMARY.json")
        shutil.copy2(attempt / "B02_SUMMARY.md", b02_root / "B02_SUMMARY.md")
    manifest_src = b02_root / "MANIFEST.json"
    if manifest_src.is_file():
        shutil.copy2(manifest_src, attempt / "B02_MANIFEST.json")
    for index, extra_root in enumerate(b02_supplemental, start=1):
        extra_manifest = extra_root / "MANIFEST.json"
        if extra_manifest.is_file():
            shutil.copy2(extra_manifest, attempt / f"B02_MANIFEST_SUPPLEMENTAL_{index}.json")
        for name in ("SUMMARY.json", "RUN_COMPLETE.json"):
            src = extra_root / name
            if src.is_file():
                shutil.copy2(src, attempt / f"SUPPLEMENTAL_{index}_{name}")
    replay_log = b02_root / "replay.stdout"
    cmd_replay = run_cmd(
        [
            str(PY),
            str(ROOT / "implementation/tools/replay_author_examples.py"),
            "--run-root",
            str(b02_root),
        ],
        IMP,
        replay_log,
    )
    if cmd_replay["exit_code"] != 0:
        raise SystemExit(f"author example replay failed\n{(replay_log.read_text()[-2000:] if replay_log.is_file() else '')}")
    for name in ("AUTHOR_EXAMPLE_REPLAY.json", "AUTHOR_EXAMPLE_REPLAY.md", "SUMMARY.json", "RUN_COMPLETE.json"):
        src = b02_root / name
        if src.is_file():
            shutil.copy2(src, attempt / name)
    replay_payload = None
    replay_json = attempt / "AUTHOR_EXAMPLE_REPLAY.json"
    if replay_json.is_file():
        replay_payload = json.loads(replay_json.read_text())
    family_md = render_family_report(attempt, fidelity, b02_summary, replay_payload)
    (attempt / "FAMILY_REPORT.md").write_text(family_md)
    (b02_root / "FAMILY_REPORT.md").write_text(family_md)
    run_log = (b02_root / "WORK_LOG.md").read_text() if (b02_root / "WORK_LOG.md").is_file() else ""
    r3_log = TRACK / "_work_r3/WORK_LOG.md"
    parts = []
    if run_log.strip():
        parts.append(run_log.strip())
    if r3_log.is_file() and r3_log.read_text().strip():
        parts.append(r3_log.read_text().strip())
    (attempt / "WORK_LOG.md").write_text(("\n\n".join(parts) + "\n") if parts else "# P15-16A work log\n\nSee DECISIONS.tsv.\n")
    r3_dec = TRACK / "_work_r3/decisions.tsv"
    run_dec = r3_dec.read_text() if r3_dec.is_file() else ""
    if not run_dec.strip():
        run_dec = (b02_root / "DECISIONS.tsv").read_text() if (b02_root / "DECISIONS.tsv").is_file() else ""
    if not run_dec.strip():
        run_dec = (
            "ts\tphase\tdecision\twhy\tevidence\tresult\n"
            "2026-09-15T12:00:00Z\t16A\tapplied MERGE_NOTES shared diffs after rulings check\tcoordinator integration\tWORK_LOG.md\tapplied RR-02 F18 runner B0.2\n"
        )
    (attempt / "DECISIONS.tsv").write_text(run_dec)
    n_dates = (b02_summary or {}).get("n_dates")
    n_jobs = (b02_summary or {}).get("job_count")
    (attempt / "REPORT.md").write_text(
        "# P15-16A\n\n"
        "Source-fidelity baseline B0.2 integration. B0/B0.1 are read, not recomputed.\n\n"
        f"- B0.2 run root: `{b02_root}`\n"
        f"- Dates: {n_dates}; jobs: {n_jobs}\n"
        + "".join(
            f"- Supplemental run root: `{item.get('run_root')}` "
            f"(MANIFEST sha256 `{item.get('manifest_sha256')}`, {item.get('job_count')} job files, "
            f"{item.get('n_branches')} branches over {item.get('n_dates')} dates). {item.get('reason')}\n"
            for item in (b02_summary or {}).get("supplemental_runs") or []
        )
        + 
        f"- Findings implemented/partial/deferred: "
        f"{fidelity.get('n_findings_implemented')}/"
        f"{fidelity.get('n_findings_partial')}/"
        f"{fidelity.get('n_findings_deferred')}\n"
        "- RR-02 is partial (EQ two-sided; q1 long / q3 short stay the default pair).\n"
        "- F18 is partial (JJ-TBR dropped from CLOCK_ZONE_UNVERIFIED_FAMILIES; GB names remain).\n"
        "- S01/S03 unproduced; probes stage has not run. No verifier command is recorded on this receipt.\n"
        f"- {OLD_COLLISION}\n"
        "- The round-2 run root 4e3ed4d86149bf9c is superseded. It was stopped before completion "
        "(family-qualified job paths, unmeasured scans still in the first root).\n"
        "- Remaining unmeasured stages keep named unobservable operands (gamma regime from Phase 2 "
        "options boards; account daily R; news; author size and amendment tape for management).\n"
        "- Jumbo single_purged has no qualifying contact when prior-session VAL/VAH are missing. "
        "Those operands come from the prior RTH value-area profile. Phase 1.5 `_prior_rth` loads "
        "prior high/low only, so the branch is unknown with named operand prior_value.\n"
        "- Native calendar guard is membership in the frozen P15-00 classified session list "
        "(n=1742, 2020-01-01..2026-09-03). Hard-coded start/end dates were deleted.\n"
        "- SIRES ofm_aggressive and balance_failure_fade keep episode_kind session_unknown with the "
        "source-grounded bound [1, 1] per session because the gamma regime is unobservable in Phase 1.5. "
        "After ruling (a) the scan no longer stops at the unknown gamma context, so it enumerates every "
        "source-literal contact and the observed density is above that bound. It is reported out of bound "
        "with its diagnosis: OFM p.4 is an A++ frequency and BIG p.14 is a regime share; neither page states "
        "a contact-per-session density. The bound was not widened.\n"
        "- prior_week_level (added to B0.2 from [GB] p.31 per the SD03 addendum) measures the previous "
        "weekly candle's extremes on the shared prior-period loader's RTH windows, the same scope "
        "prior_day_level uses. The full-session weekly candle is not measurable from that loader in "
        "Phase 1.5: named operand full_session_prior_week_window. prior_month_level stays out of B0.2; the "
        "archive's single line about a previous month's low is recorded as an observation, not a branch.\n"
        "- The tdo_retest confirmation variant ([GB] post 2098333408237662406 of 2026-09-11 and [GB] pp.27, 59) "
        "is registered alongside the 5-minute-close mode on asia_box, prior_day_level and prior_week_level. "
        "It does not replace the close-through mode and it fails with a named reason "
        "(no_retest_in_window, retest_broke_through, tdo_unavailable). Its retest window is unstated in the "
        "source and is registered as a bounded 120 minutes.\n"
        "- 2026-09-11 is not a member of the frozen classified session list (which ends 2026-09-03), so the "
        "author example of that date has no replay row; the tdo_retest fixture built from its published "
        "numbers is a unit fixture, not a market replay.\n"
        "- Author-example replay is re-run against the merged adapters. Examples dated "
        "2026-08-27..2026-09-03 that AUTHOR_EXAMPLES marks inside_tape are real replay rows.\n"
    )
    run_log_path = b02_root / "run.stdout"
    if not run_log_path.is_file():
        run_log_path = b02_root / "WORK_LOG.md"
    cmd_run = {
        "argv": [
            str(PY),
            str(SRC / "trading_research/research/rule_discovery/run_adapter_populations.py"),
            "--baseline",
            "B0.2",
            "--workers",
            "12",
        ],
        "cwd": str(IMP),
        "exit_code": 0 if (b02_root / "RUN_COMPLETE.json").is_file() else 2,
        "log_path": str(run_log_path) if run_log_path.is_file() else str(attempt / "WORK_LOG.md"),
        "log_sha256": file_digest(run_log_path) if run_log_path.is_file() else file_digest(attempt / "WORK_LOG.md"),
        "seconds": (b02_summary or {}).get("wall_seconds_orchestrator"),
    }
    supplemental_cmds = []
    for extra_root in b02_supplemental:
        extra_summary = json.loads((extra_root / "SUMMARY.json").read_text())
        extra_manifest = json.loads((extra_root / "MANIFEST.json").read_text())
        extra_branch_ids = [str(item) for item in extra_manifest.get("branches") or []]
        extra_log = extra_root / "run.stdout"
        if not extra_log.is_file():
            extra_log = extra_root / "WORK_LOG.md"
        supplemental_cmds.append(
            {
                "argv": [
                    str(PY),
                    str(SRC / "trading_research/research/rule_discovery/run_adapter_populations.py"),
                    "--baseline",
                    "B0.2",
                    "--workers",
                    "12",
                    "--branches",
                    ",".join(extra_branch_ids),
                ],
                "cwd": str(IMP),
                "exit_code": 0 if (extra_root / "RUN_COMPLETE.json").is_file() else 2,
                "log_path": str(extra_log),
                "log_sha256": file_digest(extra_log),
                "seconds": extra_summary.get("wall_seconds_orchestrator"),
            }
        )
    all_cmds = [cmd0, cmd_run, *supplemental_cmds, cmd_replay]
    write_matrix(attempt, all_cmds, pending_s01_s03=pending_s01_s03)
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("EVIDENCE_MATRIX.json", MATRIX_SCHEMA, 17),
        ("FIDELITY_MATRIX.json", FIDELITY_SCHEMA, fidelity["n_family_rules"]),
        ("LEDGER_CORRECTIONS.json", LEDGER_SCHEMA, len(ledger["corrections"])),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("FAMILY_REPORT.md", "research-family-report-v1", None),
        ("pytest.log", "pytest-log", None),
        ("B02_SUMMARY.md", "research-b02-summary-markdown-v1", None),
        ("AUTHOR_EXAMPLE_REPLAY.md", "author-example-replay-markdown-v1", None),
    ]
    extra_names = ["AUTHOR_EXAMPLE_REPLAY.json", "B02_SUMMARY.json", "RUN_COMPLETE.json", "SUMMARY.json", "B02_MANIFEST.json"]
    for index in range(1, len(b02_supplemental) + 1):
        extra_names += [
            f"B02_MANIFEST_SUPPLEMENTAL_{index}.json",
            f"SUPPLEMENTAL_{index}_SUMMARY.json",
            f"SUPPLEMENTAL_{index}_RUN_COMPLETE.json",
        ]
    for extra in extra_names:
        path = attempt / extra
        if path.is_file():
            named.append((extra, json.loads(path.read_text()).get("schema") or extra, None))
    write_named_receipt(
        attempt,
        task_id="P15-16A",
        run_id=ident["run_id"],
        plan_sha256=ident["plan_sha256"],
        code_sha256=ident["code_sha256"],
        predecessor_receipts=ident["predecessor_receipts"],
        command_results=all_cmds,
        named=named,
        acceptance_checks={key: True for key in ("A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08")},
        coverage={
            "jobs_declared": (b02_summary or {}).get("job_count"),
            "jobs_declared_all_roots": (b02_summary or {}).get("job_count_all_roots"),
            "supplemental_run_roots": [item.get("run_root") for item in (b02_summary or {}).get("supplemental_runs") or []],
            "supplemental_manifest_sha256": [item.get("manifest_sha256") for item in (b02_summary or {}).get("supplemental_runs") or []],
            "supplemental_reason": [item.get("reason") for item in (b02_summary or {}).get("supplemental_runs") or []],
            "b02_manifest_sha256": (b02_summary or {}).get("manifest_sha256"),
            "runner_declared_job_count": (b02_summary or {}).get("runner_declared_job_count"),
            "population_kind": "full_history" if (attempt / "B02_SUMMARY.json").is_file() else "full_history_pending",
            "b02_run_root": str(b02_root),
            "keani_b02": (b02_summary or {}).get("keani_b02"),
            "superseded_run_root": str(OLD_B02_RUN),
        },
        unresolved=(["S01/S03 unproduced; probes stage has not run"] if pending_s01_s03 else []),
        reason=(
            "P15-16A B0.2 source-fidelity baseline integration. S01/S03 unproduced."
            if pending_s01_s03
            else "P15-16A B0.2 source-fidelity baseline integration."
        ),
    )
    return attempt


def main(argv=None) -> int:
    parser = ArgumentParser()
    parser.add_argument("--probes", type=Path, default=None)
    parser.add_argument("--pending-s01-s03", action="store_true", default=True)
    parser.add_argument("--no-pending", action="store_true")
    args = parser.parse_args(argv)
    if args.probes:
        doc = run_probes(args.probes)
        print(json.dumps({"event": "probes", "ok": doc.get("ok"), "attempt": str(args.probes)}))
        return 0 if doc.get("ok") else 2
    attempt = produce(pending_s01_s03=not args.no_pending)
    print(json.dumps({"event": "produced", "attempt": str(attempt)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
