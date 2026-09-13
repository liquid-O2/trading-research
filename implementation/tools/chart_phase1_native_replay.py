#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from trading_research.research.method_pack.historical_charts import render
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);args=p.parse_args()
    out=render(args.run_root);print('charts:',len(out['examples']))
