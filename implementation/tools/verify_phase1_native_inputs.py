#!/usr/bin/env python3
"""Read-only native integration proof for the Phase 1 v2 run."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from trading_research.research.method_pack.historical_integration import run_integration
if __name__=='__main__':
    report=run_integration()
    print('native integration',report['report_sha256'])
