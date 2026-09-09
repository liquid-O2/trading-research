# Research period

The user's 2026-09-07 instruction sets the primary model population to **2020-01-01 onward**, through the latest eligible observations actually available at each frozen evaluation cut. Subsequent primary model training, calibration and evaluation registrations must use that population. Missing observations and future time remain explicit dependencies.

Older data may support selected Jumbo constructions and ordinary OHLC context or comparisons. Each such use keeps its own declared purpose and cohort; it does not expand the denominator of primary model results. Older data is optional for those uses, so it does not hold up independent work on the main model.

The machine-readable policy is [research-period.json](configs/research-period.json). Existing source files, planning manifests, registrations and historical engineering/data-audit receipts remain intact. No market-model evaluation has yet been completed under this period policy.
