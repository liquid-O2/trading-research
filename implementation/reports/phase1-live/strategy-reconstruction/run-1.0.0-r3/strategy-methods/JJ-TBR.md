# JJ-TBR: strategy reconstruction

Observed entry candidates: 14 setup, 67 no setup, 8 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| judas_outbound | entry_setup | TBR pp.8–10: pre-open direction → 09:30 outbound → selected exhaustion → exit by reversal window |
| judas_reversal | entry_setup | TBR pp.8–11,27–29: frozen range/context → edge sweep → 09:40–09:50 block/rejection → opposing draw |
| single_extended | entry_setup | TBR pp.12–14,24: extended overnight → EQ/quadrant → directional confirmation → range-edge target/reduced expectation |
| single_purged | entry_setup | TBR pp.12–15: dated prior-liquidity purge → compressed range → internal contact/confirmation → expansion |
| internal_rotation | entry_setup | JR pp.3,38–43;TBR pp.12,24: wide balanced context → named internal → actual reversal signature → nearer named target |
| extension_reaction | entry_setup | TBR pp.20–21;JR pp.23–26,57: prior expansion → actual parent 1.33–1.66 projection → response → still-unused objective |
| other_session | entry_setup | TBR p.7,36;JR pp.46,50–51: one of seven published formations → fixed context/location → selected confirmation/risk/objective |
| timed_pzone_reversal | entry_setup | JR pp.16–18,53–55,58–62: dated supplied P-zone → contact → reversal → directed named destination |
| management | personal_execution_out_of_scope | FORMULAS:M01: management process/management unit |

Operational model (pzone): `{'source': 'JJumboFX_Raw_X_Archive_v2.pdf pp.16–18,53–55,60–61', 'lookback_sessions': 500, 'minimum_sessions': 20, 'anchors': ['02:00', '09:00', '10:00'], 'quantiles': [0.7, 0.8], 'volume_filter': 'historical session volume at least median of prior training sessions', 'distance': 'maximum up/down move from anchor to 16:00 divided by pre-anchor 60-minute range', 'live_scale': 'current completed pre-anchor 60-minute range; quarter-point outward rounding', 'target': 'frozen anchor price; support and resistance evaluated only toward anchor', 'clock': 'historical minute-bar training only, prior dates; live anchor uses event-time bars'}`

Operational model (calendar): `{'model': 'regular NQ schedule with inferred New Year/Christmas RTH closures', 'scope': 'fixed-date New Year/Christmas closures, including Monday observance; Friday before Saturday New Year remains regular, corroborated by 390 native 2021-12-31 RTH minute records; other unverified holidays remain unavailable', 'interpretation': 'reconstruction calendar assumption, not newly recovered CME schedule evidence'}`

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| other_session | no_setup | source_confirmation | 37 |
| other_session | no_setup | risk_defined | 12 |
| timed_pzone_reversal | no_setup | source_confirmation | 10 |
| extension_reaction | no_setup | source_confirmation | 7 |
| extension_reaction | no_setup | reaction_side_confirmed | 7 |
| judas_reversal | no_setup | source_confirmation | 4 |
| internal_rotation | no_setup | rotation_context | 4 |
| extension_reaction | no_setup | risk_defined | 3 |
| extension_reaction | no_setup | objective_is_remaining_draw | 3 |
| other_session | data_unavailable | source_confirmation | 3 |
| other_session | data_unavailable | risk_defined | 3 |
| other_session | data_unavailable | objective_fixed | 3 |
| other_session | data_unavailable | confirm_at | 3 |
| other_session | data_unavailable | confirm_at touch_at | 3 |
| other_session | data_unavailable | confirm_at decision_at | 3 |
| timed_pzone_reversal | no_setup | risk_defined | 3 |
| judas_outbound | no_setup | risk_defined | 2 |
| internal_rotation | no_setup | source_confirmation | 2 |
| judas_outbound | data_unavailable | source_confirmation | 1 |
| judas_outbound | data_unavailable | risk_defined | 1 |
| judas_outbound | data_unavailable | objective_fixed | 1 |
| judas_reversal | data_unavailable | context_fixed | 1 |
| judas_reversal | data_unavailable | reversal_context | 1 |
| judas_reversal | no_setup | risk_defined | 1 |
| judas_reversal | data_unavailable | source_confirmation | 1 |
| judas_reversal | data_unavailable | risk_defined | 1 |
| judas_reversal | data_unavailable | objective_fixed | 1 |
| judas_reversal | data_unavailable | confirm_at | 1 |
| judas_reversal | data_unavailable | confirm_at touch_at | 1 |
| judas_reversal | data_unavailable | confirm_at decision_at | 1 |
| judas_reversal | data_unavailable | confirm_at sweep_at | 1 |
| single_extended | no_setup | source_confirmation | 1 |
| single_extended | data_unavailable | source_confirmation | 1 |
| single_extended | data_unavailable | risk_defined | 1 |
| single_extended | data_unavailable | objective_fixed | 1 |
| single_extended | data_unavailable | confirm_at | 1 |
| single_extended | data_unavailable | confirm_at touch_at | 1 |
| single_extended | data_unavailable | confirm_at decision_at | 1 |
| single_purged | no_setup | source_confirmation | 1 |
| single_purged | data_unavailable | source_confirmation | 1 |
| single_purged | data_unavailable | risk_defined | 1 |
| single_purged | data_unavailable | objective_fixed | 1 |
| single_purged | data_unavailable | confirm_at | 1 |
| single_purged | data_unavailable | confirm_at touch_at | 1 |
| single_purged | data_unavailable | confirm_at decision_at | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/methods/JJ-TBR.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/registry/STRATEGY_POLICY.json).
