"""Single-core B0.2 candidate-pipeline measurement. One process. Load once per date."""
from __future__ import annotations

from pathlib import Path
import cProfile
import json
import pstats

from trading_research.research.rule_discovery.search import (
    THROUGHPUT_CANDIDATE_IDS,
    load_b02_market,
    measure_throughput,
    resolve_bank,
    scan_candidate,
)
from trading_research.research.rule_discovery.source_adapters.common import install_write_guard

ROOT = Path(__file__).resolve().parent
PROFILE_DAY = "2024-01-02"
PROFILE_CANDIDATE = "GB-FAIL:nyam_box:F1"


def main() -> None:
    install_write_guard()
    document = measure_throughput()
    path = ROOT / "THROUGHPUT_B02.json"
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    resolved = {item.candidate_id: item for item in resolve_bank()}
    market = load_b02_market(PROFILE_DAY)
    profiler = cProfile.Profile()
    profiler.enable()
    scan_candidate(market, resolved[PROFILE_CANDIDATE])
    profiler.disable()
    profile_path = ROOT / "PROFILE_B02.txt"
    with profile_path.open("w") as handle:
        handle.write(f"candidate {PROFILE_CANDIDATE} date {PROFILE_DAY} (scan only; load excluded)\n")
        stats = pstats.Stats(profiler, stream=handle)
        stats.sort_stats("cumulative")
        stats.print_stats(20)
    print(json.dumps({"throughput": str(path), "profile": str(profile_path), "p90": document["pipeline_p90_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
