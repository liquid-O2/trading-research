from pathlib import Path
from trading_research.research.method_pack.historical_runner import date_job,immutable_json,file_digest,load_registry
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--run-root',default=str(Path(__file__).resolve().parents[1]));args=parser.parse_args()
root=Path(args.run_root)
directory=root/'jobs/evaluation/2020-01-02'
paths=sorted(directory.glob('*'));assert len(paths)==56
before={str(p):file_digest(p) for p in paths}
result=date_job(root,'evaluation','2020-01-02')
after={str(p):file_digest(p) for p in paths}
assert before==after and result['branches']==55
reg,_=load_registry(root)
immutable_json(root/'validation/resume-verification.json',{'status':'pass','registry_sha256':reg['registry_sha256'],'cohort':'evaluation','date':'2020-01-02','unchanged_artifacts':len(paths),'sha256_by_path':before,'result':result})
print('55 completed jobs and their completion receipt are unchanged after validated resume.')
