"""Method inventories and branch lists from FORMULAS."""

from __future__ import annotations

import json
from pathlib import Path

_EXTRACT = json.loads(Path(__file__).with_name("catalog_extract.json").read_text())
METHOD_OBJECTS = {key: list(value) for key, value in _EXTRACT["methods"].items()}
OBJECT_META = _EXTRACT["objects"]

METHOD_BY_ID = {
    "JJ-TBR": "M01",
    "GB-FAIL": "M02",
    "GB-VWAP": "M03",
    "GB-SCALP": "M04",
    "SIRES": "M05",
    "SAINT-AMT": "M06",
    "MEMBER-TWO-REASONS": "M07",
    "KEANI-OPEN-ABOVE-VALUE": "M08",
    "REFILL-STUDY": "M09",
    "JETBUNDLE-STATES": "M10",
    "STOIC-DATA": "M11",
    "STOIC-RISK": "M12",
}

BRANCHES = {
    "JJ-TBR": [
        "judas_outbound", "judas_reversal", "single_extended", "single_purged",
        "internal_rotation", "extension_reaction", "other_session", "timed_pzone_reversal",
    ],
    "GB-FAIL": [
        "nyam_box", "previous_hour", "asia_tdo_case", "prior_day_level",
        "prior_week_level", "prior_month_level", "cash_open_reclaim_case", "mss_fvg_refinement",
    ],
    "GB-VWAP": ["source_long"],
    "GB-SCALP": ["bearish_small_scalp", "bullish_discount_pullback"],
    "SIRES": [
        "dom_rejection", "absorption_reward_retest", "stop_four_stage",
        "footprint_confirmed_reaction", "vwap_deviation_fade", "ofm_aggressive",
        "ofm_passive", "clean_squeeze", "balance_failure_fade",
        "defended_band_continuation", "microbalance_break", "kg1_retest",
    ],
    "SAINT-AMT": ["continuation_retest", "trapped_buyers_retest", "failed_auction_return", "poc_traversal"],
    "MEMBER-TWO-REASONS": ["resistance_short", "planned_return_long"],
    "KEANI-OPEN-ABOVE-VALUE": ["source_long"],
    "REFILL-STUDY": ["touch_record", "supplied_selected_order"],
    "JETBUNDLE-STATES": ["B", "A", "D", "E", "W"],
    "STOIC-DATA": ["process_review", "macro_application"],
    "STOIC-RISK": ["first", "second", "reset_after_second_win"],
}

PRIMARY = {
    "JJ-TBR": "sequence",
    "GB-FAIL": "sequence",
    "GB-VWAP": "sequence",
    "GB-SCALP": "case_description",
    "SIRES": "sequence",
    "SAINT-AMT": "sequence",
    "MEMBER-TWO-REASONS": "sequence",
    "KEANI-OPEN-ABOVE-VALUE": "sequence",
    "REFILL-STUDY": "touch_causality",
    "JETBUNDLE-STATES": "state_observation",
    "STOIC-DATA": "process",
    "STOIC-RISK": "printed_ladder",
}

EXTRA_PREDICATES = {
    "JJ-TBR": ["management"],
    "GB-SCALP": ["automatic_admission"],
    "SIRES": ["case_description", "management", "reentry"],
    "REFILL-STUDY": ["selected_order_configuration"],
    "JETBUNDLE-STATES": ["transition_observation"],
    "STOIC-DATA": ["macro_application"],
}

ENGINE_HOLE_BRANCHES = {
    "JJ-TBR": ("timed_pzone_reversal", "internal_rotation"),
    "GB-FAIL": ("asia_tdo_case",),
    "GB-VWAP": (),
    "GB-SCALP": ("bullish_discount_pullback",),
    "SIRES": ("kg1_retest",),
    "SAINT-AMT": (),
    "MEMBER-TWO-REASONS": (),
    "KEANI-OPEN-ABOVE-VALUE": (),
    "REFILL-STUDY": (),
    "JETBUNDLE-STATES": (),
    "STOIC-DATA": ("macro_application",),
    "STOIC-RISK": (),
}

DISCOVERY = {
    "JJ-TBR": "hole",
    "GB-FAIL": "hole",
    "GB-VWAP": "hole",
    "GB-SCALP": "hole",
    "SIRES": "hole",
    "SAINT-AMT": "hole",
    "MEMBER-TWO-REASONS": "hole",
    "KEANI-OPEN-ABOVE-VALUE": "hole",
    "REFILL-STUDY": "hole",
    "JETBUNDLE-STATES": "hole",
    "STOIC-DATA": "hole",
    "STOIC-RISK": "hole",
}

DISCOVERY_REASON = {
    "JJ-TBR": "source context/location/confirmation selectors unpublished",
    "GB-FAIL": "source session/bias/admission selector and several reference clocks remain holes",
    "GB-VWAP": "source session bounds, breakout-bar definition, VWAP reset/basis unpublished",
    "GB-SCALP": "no repeatable source-complete scalp selector",
    "SIRES": "auction bands, qualitative flow, CVD reference, proprietary levels unpublished",
    "SAINT-AMT": "automatic balance/control/acceptance selectors incomplete",
    "MEMBER-TWO-REASONS": "automatic reaction/node selection unpublished",
    "KEANI-OPEN-ABOVE-VALUE": "value/imbalance settings and near-10:00 timing unpublished",
    "REFILL-STUDY": "cluster/normalization, hold label, grade model unpublished",
    "JETBUNDLE-STATES": "Native event coverage and heuristic classifier rules incomplete; AAPL is illustrative",
    "STOIC-DATA": "full trading recipe and custom macro engines unpublished",
    "STOIC-RISK": "only printed-stage arithmetic reconstructable; Monte Carlo unpublished",
}


def objects_for(method_id: str) -> list[str]:
    return list(METHOD_OBJECTS[METHOD_BY_ID[method_id]])
