#!/usr/bin/env python3
"""Rerun preserved acceptance counterexamples into separate empirical evidence."""
from pathlib import Path
import importlib.util
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'implementation/src'))
OUTPUT=ROOT/'implementation/reports/phase1-live/empirical/validation'


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    probe=load(ROOT/'implementation/validation/phase1-post-implementation-check/original-check/probe_lifecycles.py','empirical_original_probe')
    probe.__file__=str(OUTPUT/'probe_lifecycles.py')
    assert probe.main()==0
    post=load(ROOT/'implementation/tools/validate_phase1_post_implementation_regressions.py','empirical_post_regression')
    post.REPORT=OUTPUT/'repair-regressions.json'
    assert post.main()==0
    audit=load(ROOT/'implementation/tools/validate_phase1_audit_regressions.py','empirical_audit_regression')
    audit.OUTPUT=OUTPUT/'audit-regressions.json'
    assert audit.main() in (0,None)


if __name__=='__main__':main()
