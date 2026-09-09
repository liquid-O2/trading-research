# Every component and named refinement has an experiment record

There are **153 parent contracts**, **191 named refinement experiments**, and **2,752 explicit phase records** across 344 units. This counts test plans, not trained models, independent discoveries, passing tests or mandatory production components.

| Family | Parent contracts | Named refinements | Individual phases |
|---|---|---|---|
| [Data, clocks and state](F.md) | 12 | 12 | 192 |
| [Flow, profile and market measurements](M.md) | 13 | 19 | 256 |
| [Context and volatility](C.md) | 24 | 46 | 560 |
| [Options, surfaces, flow and nodes](O.md) | 23 | 28 | 408 |
| [Cross-market information](X.md) | 10 | 19 | 232 |
| [Location and opportunity generation](L.md) | 19 | 20 | 312 |
| [Mixtures, calibration and selection](G.md) | 10 | 11 | 168 |
| [Policy, execution and account risk](P.md) | 12 | 13 | 200 |
| [Deferred Response mechanisms](R.md) | 22 | 14 | 288 |
| [Research evidence and operations](V.md) | 8 | 9 | 136 |

Machine-readable [experiment registry](../review/third-review/experiment_registry.json) and manually curated [refinement definitions](../review/third-review/specialists.tsv) preserve the same IDs, targets, fixtures, challengers and gates. The generator reads current parent cards so their local cases remain attached to each parent; substantive refinement definitions are authored separately, not inferred from keywords. The [full-system contract refinements](../SYSTEM_REFINEMENT.md), [153 upgrade paths with 191 specific child bindings](../UPGRADE_PATHS.md) and [implementation constructions](../UPGRADE_CONSTRUCTIONS.md) bind every unit and are carried into local definition/reference/comparison/interaction phases.

The [conversation recheck](../CONVERSATION_RECHECK.md) maps all 122 conversation findings to specific experiment units or explicit provenance/dependency cases. The original 712-source and 114-external matrices remain authoritative for exact source clauses.
