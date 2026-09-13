#!/usr/bin/env python3
"""Final selected-root native controls and full test suite."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from trading_research.research.method_pack.historical_validation import run_controls,full_suite

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',required=True)
    parser.add_argument('--part',choices=('controls','suite','all'),default='all');args=parser.parse_args()
    if args.part in ('controls','all'):print(json.dumps(run_controls(args.run_root),indent=2),flush=True)
    if args.part in ('suite','all'):print(json.dumps(full_suite(args.run_root),indent=2),flush=True)
