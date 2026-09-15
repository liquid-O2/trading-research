# Track R1 candidate verdicts

family | branch | B0.1 n | B0.1 unknown | cand n | cand unknown | B0.1 share | cand share | rule
--- | --- | --- | --- | --- | --- | --- | --- | ---
JJ-TBR | judas_reversal | 10 | 0 | 240 | 0 | 0.000 | 0.000 | baseline_repairs.py:547 O056 full-C2 _ob_repaired
GB-FAIL | nyam_box | 10 | 0 | 184 | 0 | 0.000 | 0.000 | baseline_repairs.py:836 first complete five-minute reclaim
GB-VWAP | source_long | 4 | 0 | 224 | 0 | 0.000 | 0.000 | baseline_repairs.py:951 later VWAP retest
SIRES | absorption_reward_retest | 12 | 0 | 84 | 0 | 0.000 | 0.000 | baseline_repairs.py:317 flow_stages selected stage
SAINT-AMT | continuation_retest | 9 | 0 | 84 | 0 | 0.000 | 0.000 | historical_auction_scanners.py:16 two-bar body/delta control
MEMBER-TWO-REASONS | planned_return_long | 5 | 0 | 84 | 0 | 0.000 | 0.000 | baseline_repairs.py:1140 defense or rejection after contact
KEANI-OPEN-ABOVE-VALUE | source_long | 8 | 0 | 180 | 0 | 0.000 | 0.000 | baseline_repairs.py:1211 imbalance-band defense
REFILL-STUDY | touch_record | 0 | 0 | 84 | 0 | 0.000 | 0.000 | baseline_repairs.py:1284 distinct return after departure

## F1 and R counts by verdict

All-family F1 {'episodes': 672, 'unknown': 0, 'setup': 24, 'no_setup': 564}
All-family R {'episodes': 492, 'unknown': 0, 'setup': 6, 'no_setup': 486}
All-family B0.1 {'episodes': 58, 'unknown': 0, 'setup': 12, 'no_setup': 46}

JJ-TBR primary (orchestrator cited 84 F1 and 156 R against B0.1 10):
F1 {'episodes': 84, 'setup': 0, 'no_setup': 84, 'unknown': 0, 'pass': 0, 'fail': 84}
R {'episodes': 156, 'setup': 0, 'no_setup': 156, 'unknown': 0, 'pass': 0, 'fail': 156}
B0.1 {'episodes': 10, 'setup': 0, 'no_setup': 10, 'unknown': 0, 'pass': 0, 'fail': 0}

Measured counts restated by verdict. Unknown share uses strategy_assessment status.

Pytest: 320 passed in 783.45s. `tests/rule_discovery -q -p no:cacheprovider`
