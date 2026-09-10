#!/usr/bin/env python3
"""Phase 1 live object runner. Modes: check, run, report."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_research.research.phase1_live.runner import main

if __name__ == "__main__":
    raise SystemExit(main())
