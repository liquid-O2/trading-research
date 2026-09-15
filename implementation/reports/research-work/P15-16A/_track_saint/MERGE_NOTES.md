# Merge notes (saint track)

No shared-file patch. `common.py`, `confirmation.py`, `run_adapter_populations.py`, and `tools/` were not edited. B0.2 lives on family adapters plus `source_adapters/b02_saint_track.py` (this track only).

Integration still needs to call `scan_b02(market, rec)` and `replay_example(market, example)` per family after importing the adapter module.
