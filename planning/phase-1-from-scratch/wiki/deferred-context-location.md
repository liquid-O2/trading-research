# Phase 2–3 handoff: emitted columns and objects

This is the entire later-phase design scope. The current task limits Phase 2 to Context and Phase 3 to Location. Historical user intent is in [Develop Trading Model, user L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md), [raw log, user L143–178](../../../sources/documents/conversations/conversation_raw_log.md), and [feature-level design, user L1560–1854](../../../sources/documents/conversations/Design%20robust%20feature%20levels.md). Their older assistant model designs are unapproved.

| Consumer | Phase 1 emits | Availability rule |
|---|---|---|
| Context | Session/instrument/calendar IDs; faithful and experimental Jumbo/AMT/path labels; break order and final extreme times | Completed labels are targets, never earlier features |
| Context | Width/balance/extension, clean edges, open versus prior RTH range/value, sister-market nonconfirmation, prior available events | Snapshot at the stated observation time |
| Context | GK/YZ/RV/HAR lagged inputs, IV/skew/VX descriptors, profile shape/migration, all five CVD constructions and raw auction-state components | Per-feature known_at and missingness |
| Context | Remaining-path outcomes at defined horizons; censoring; eligible/matched population and discovery/confirmation IDs | Future outcomes remain separate |
| Location | Frozen range/internal/liquidity rails; extensions; faithful Jumbo P-zones and measured approximation variants | P-zones remain distinct from extensions |
| Location | VP/VA/POC, delta profiles, shelves/ledges/HVN/LVN, TPO, VWAP bands, confirmed swing/FVG/CISD blocks | Bounds, source/variant, creation and confirmation times |
| Location | Options/flow nodes, strength, expiry/scenario, mapped/native prices, density, age, prior tests, arrival state | Versioned identity; no future node revisions |
| Location | Touch/reject/overshoot/acceptance/path reports for every measured variant; source disagreements and uncertainty | Winners are conditional evidence, not mandatory selectors |

Phase 2 may later predict context. Phase 3 may later learn which zone deserves action, including adaptive reversal/P-zone selection. Phase 1 does not train or deploy those models, design entries/stops/sizing, or validate the later P&L target. Source risk/psychology advice is deferred ([code-2-risk, pp.3–7](../../../sources/documents/discretionary/code-2-risk.pdf#page=3); [emotion, pp.1–9](../../../sources/documents/discretionary/emotion.pdf#page=1)). Skylit, Heatseeker, Flowseeker and Atlas are not reviewed here.

[Measurement contract](measurement-contract.md) · [Wiki index](index.md)
