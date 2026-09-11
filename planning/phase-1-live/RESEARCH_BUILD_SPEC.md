# Research build specification: the 85 main models

Status: **specification complete and checked**. All 85 main models have buildable research definitions. Replacement engines have not been implemented or backtested by this task.

This handoff defines the next research implementation for Jumbo, Green Bird, auction/profile, order flow, regime and Sires. It excludes all 20 PineScript rows. The user authorized explicit assumptions and bounded experiments for unpublished methods on 2026-09-11. An assumption in this specification is therefore implementable without asking for the original author's settings. It is a new research definition, not a claim to have recovered a hidden formula.

“Better” has two separate tests: the implementation must first be mathematically consistent, causal and reproducible; a candidate must then earn an empirical improvement claim under the comparison protocol. More parameters or closer agreement with a selected screenshot do not establish improvement.

The completed [chart audit](CHART_AUDIT.md) remains the record of the old implementation and source discrepancies. Its unresolved questions do not block the named research definitions here. Do not silently change that audit's historical verdicts. Do not use the existing booleans, fixtures or published win percentages as ground truth for the replacement engine.

Read and implement in this order:

1. [Data contracts](research-spec/DATA_CONTRACTS.md): actual stored inputs, normalization, availability, quality and acquisition alternatives.
2. [Shared engines](research-spec/ENGINES.md): equations, clocks, lifecycle rules, event ordering and common execution semantics.
3. [Experiment protocol](research-spec/EXPERIMENT_PROTOCOL.md): bounded grids, controls, chronological selection and promotion criteria.
4. [Model cards](research-spec/MODEL_CARDS.md): all 85 IDs, exact defaults, algorithms, consumers, outputs and acceptance cases. The machine-readable authority is [model_specs.json](research-spec/model_specs.json).
5. [Implementation handoff](research-spec/IMPLEMENTATION_HANDOFF.md): dependency order, file responsibilities, commands to provide and acceptance gates.

The package declares 293 parameters and 593 default/one-factor configurations before bounded interactions. It includes 31 checked numerical examples, model-specific acceptance requirements, and both required family status tables. [Validation results](research-spec/validation.json) distinguish specification checks from future engine tests. The [JSON Schema](research-spec/model_specs.schema.json) validates the machine-readable contract; [delivery hashes](research-spec/delivery_manifest.json) identify the frozen files.

Regenerate the compiled cards/configuration with `python implementation/tools/research_spec_build.py`, then check them with `python implementation/tools/research_spec_validate.py` from `/workspace`. The checker requires the `jsonschema` Python package. It also verifies dependency order, parameter grids, local links and preserved audit/input hashes. These commands do not run trading models.

The JSON parameters and model-specific instructions override a shared default only when the card explicitly binds that parameter. Neither free parameter searches nor implicit fallback formulas are permitted. Missing data produces a typed unavailable state. It must never become a false event, neutral regime or zero-volume confirmation.

Research is initially for one NQ contract as the execution unit, with ES/YM/RTY and native option underlyings used only in their own price coordinates when required. This is a research unit, not an account-sizing recommendation. Contract specifications and the active raw contract come from the input manifest. Source examples in MNQ, ES, GC, SPX, SPY or QQQ are not exact NQ fixtures.

The user's first-revisit requirement is mandatory: each external high and low ends independently at its first post-formation revisit, including overnight trading. A sweep can start an episode that confirms later; it cannot make the consumed high or low fresh again. Open-price references, profile areas, FVGs and model-generated statistical bands have separately defined lifecycles.

Give the next model the [ready-to-use implementation task](research-spec/IMPLEMENTATION_HANDOFF.md#6-ready-to-use-implementation-task). It specifies the full build, meaningful correctness tests and bounded comparisons needed to assess improvement.
