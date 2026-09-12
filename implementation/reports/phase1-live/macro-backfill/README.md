# Macro vintage backfill for the NQ study

The identified FRED collection has been backfilled: **20 series, 37,003 vintage records, including 35,823 nonmissing value versions and 31,121 confirmed initial values**. The vintage window is January 1, 2020 through September 12, 2026. Original files under `/workspace/data` were not changed. Credentials are absent from the saved requests, responses and manifests.

The collection includes the 18 FRED series already named by the acquired archive, plus CPIAUCSL and PAYEMS, identified through its CPI/payroll release calendars. This is a provider-data collection; it does not invent the series list, transforms or thresholds of an author's proprietary macro model.

The main bundle contains reference periods from January 2020 onward. A small supplementary bundle holds December 2019 CPI/payroll observations, first released in January 2020, so those releases are included in the trading window. The supplement contains 15 versions of two observations. It does not extend the NQ market study before 2020.

| Saved result | Contents |
|---|---|
| [Main acquisition manifest](/workspace/implementation/reports/phase1-live/macro-backfill/fred-h233aw4x/manifest.json) | 20 series; 36,988 observation/vintage records; metadata, initial releases, complete real-time intervals and vintage-date pages |
| [Main normalized manifest](/workspace/implementation/reports/phase1-live/macro-backfill/fred-h233aw4x/normalized-p0wb8u84/manifest.json) | One JSONL per series; native values/units, reference periods, immutable version IDs and separate publication/availability fields |
| [January-release supplement](/workspace/implementation/reports/phase1-live/macro-backfill/fred-lkh5q0xl/manifest.json) | December 2019 CPI/payroll observations and their subsequent revisions |
| [Supplement normalized manifest](/workspace/implementation/reports/phase1-live/macro-backfill/fred-lkh5q0xl/normalized-nvnc16ew/manifest.json) | Two additional JSONL files, with disjoint reference periods from the main bundle |
| [Verification and per-series counts](/workspace/implementation/reports/phase1-live/macro-backfill/verification.json) | Source/artifact checksums, pagination/count checks, code hashes, causal checks and test result |

Use both normalized bundles. They have no duplicate `(series, reference period, vintage)` keys. The earlier small [capability probe](/workspace/implementation/reports/phase1-live/macro-source-check/README.md) is a demonstration and is not an additional input partition.

## Coverage

All 104 authenticated FRED requests succeeded. Every declared result count and pagination offset reconciles with the saved responses. Coverage ends at each series' last published observation, not automatically at the requested end date. CPI/payroll reach the August 2026 reference month; daily series reach September 4, 10 or 11 according to their source release cycle. Values published after the acquired NQ endpoint remain unavailable to earlier NQ decisions.

The exact series are CPIAUCSL, PAYEMS, DEXJPUS, DFF, DGS1, DGS1MO, DGS3MO, DGS6MO, DGS10, DTB3, DTWEXAFEGS, EFFR, GVZCLS, RVXCLS, SOFR, T10YIE, VIXCLS, VXDCLS, VXNCLS and VXVCLS. CPIAUCSL is a seasonally adjusted price index and PAYEMS is a payroll employment level, in their native units. These are not consensus forecasts or automatically constructed news surprises.

The 1,180 provider missing-value records are retained as `value=null` with the original `fred_value="."`; they are never interpolated. Most belong to daily series' nonreporting dates. **October 2025 CPI is a genuine publisher gap.** BLS suspended collection during the funding lapse and did not issue that month's CPI release. See the [BLS explanation](https://www.bls.gov/cpi/additional-resources/2025-federal-government-shutdown-impact-cpi.htm). FRED also does not confirm an initial nonmissing value for 22 daily series/reference-period pairs even though their later value histories exist; the verification file lists them. No later value was relabeled as their initial release.

## Publication clocks and what remains unknown

**160 distinct BLS publication dates were individually verified, covering 161 initial CPI/payroll observations.** One payroll publication contains two reference months. Each clock comes from its own dated BLS news-release embargo header, with the stated Eastern timezone checked against daylight saving time. Evidence is saved in the main and supplementary `bls-publication-evidence.json` files; validated clocks are in each normalized bundle's `release-clocks.json`.

`released_at` is the verified publisher clock, in UTC nanoseconds, plus an ISO UTC representation. `available_at` and `known_at` remain null because a publication clock does not establish arrival at a trading feed. O162 can use the publication clock only with the explicit `release_as_availability=True` assumption. Date-only vintages and revisions without value-specific clock evidence retain their timing holes. A revision never inherits the initial release's time.

The remaining **36,842 records have date-level vintage evidence only**; that count includes missing-value records. They support civil-date historical snapshots. They do not independently support an intraday decision. [FRED real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) use dates, and its [observation API](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) supplies distinct initial-release and real-time-period outputs. No release time, fixed lag or midnight availability was invented.

The `releases_for_decision()` helper prepares matching series/reference-period records for O162, excluding future vintage dates while retaining relevant unknown clocks. A latest-vintage query remains unknown when an applicable revision has no clock. `initial_only=True` is appropriate only when the research question explicitly asks for the initial release. `vintage_on_date()` is a date-level snapshot helper, not an intraday availability adapter.

## Reproduction and validation

Run [backfill_macro_vintages.py](/workspace/implementation/tools/backfill_macro_vintages.py) from `/workspace` with `--data-root /workspace/data --output-root /workspace/implementation/reports/phase1-live/macro-backfill --start 2020-01-01 --end 2026-09-12`. It reads `FRED_API_KEY` from the environment or prompts with hidden input. It creates a new directory and refuses output inside the raw data root, including through symlinks.

For the January-release supplement, add `--reference-start 2019-12-01 --reference-end 2019-12-31 --series CPIAUCSL PAYEMS`. Reference periods and vintage dates are deliberately separate arguments.

Run [normalize_macro_vintages.py](/workspace/implementation/tools/normalize_macro_vintages.py) with `--bundle <new-acquisition-directory> --data-root /workspace/data --clock-evidence <matching-bls-publication-evidence.json>`. Supply only the individually verified clocks matching that bundle's candidates; omitted clocks remain explicitly unresolved. The saved evidence can reproduce this acquisition window. A later window requires checking any new publication dates.

**214 tests and two subtests passed, including 13 macro-backfill tests.** Validation checks all 104 response artifacts, all 24 normalized artifacts, every normalized row against the current implementation, and the unchanged hashes/timestamps of 31 original archive files. It also exercises the actual CPI release boundary: one nanosecond before release is unavailable; the release instant is usable only under the explicit availability assumption; a later unknown-clock revision blocks the latest-vintage view. A September 11, 2026 release is excluded from September 3 NQ decisions. Test counts and code hashes are recorded in the verification file.

This closes the acquisition gap for these identified series and initial BLS publication clocks. Exact revision/other-series intraday clocks, observed feed arrival, consensus expectations and unpublished author rules remain separate requirements when a selected branch needs them. It does not populate historical method cohorts. See the [cohort explanation](/workspace/implementation/reports/phase1-live/cohort-status.md).
