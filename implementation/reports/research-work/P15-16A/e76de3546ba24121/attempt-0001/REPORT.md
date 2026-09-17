# P15-16A

Source-fidelity baseline B0.2 integration. B0/B0.1 are read, not recomputed.

- B0.2 run root: `/workspace/implementation/reports/research-work/P15-16A/1e13829f2c88f1e1`
- Dates: 1742; jobs: 66196
- Findings implemented/partial/deferred: 37/2/4
- RR-02 is partial (EQ two-sided; q1 long / q3 short stay the default pair).
- F18 is partial (JJ-TBR dropped from CLOCK_ZONE_UNVERIFIED_FAMILIES; GB names remain).
- S01/S03 unproduced; probes stage has not run. No verifier command is recorded on this receipt.
- KEANI-OPEN-ABOVE-VALUE B0.2 is not measured: job files are `jobs/<date>/<branch>.json.gz`, which collides with GB-VWAP `source_long`. Distinct job files: 66196; runner declared 67938.
