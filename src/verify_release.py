"""Read-only independent score recomputation, trace hashes and direct-law replay."""
import json
from pathlib import Path
import numpy as np
from src.common import ROOT,sha
from gop_intake.__main__ import verify

def verify_all():
 checks={};counts=0;maxerr=0.
 for split in ['development','calibration','final']:
  for line in (ROOT/f'results/direct_generator/{split}.jsonl').read_text().splitlines():
   r=json.loads(line);p=ROOT/r['prediction_file']
   with np.load(p,allow_pickle=False) as z:
    hs=list(z['horizons']);models=['F2','no_lift_quadratic','linear_drift','sparse_degree7','F0_P_legacy','persistence','training_mean']
    j=hs.index(r['horizon']);k=models.index(r['model']);a=z['pred'][j,k];b=z['target'][j];valid=z['mask'][j]
    bad=~np.isfinite(a)|(np.abs(a)>1e6);loss=np.where(bad,1e12,np.minimum((a-b)**2,1e12));mse=float(np.mean(loss[valid]));maxerr=max(maxerr,abs(mse-r['mse']))
    if mse!=r['mse'] or int(bad[valid].sum())!=r['divergences']:raise ValueError('score mismatch')
   counts+=1
 trace_count=0
 for p in list((ROOT/'results/direct_generator').glob('*_trace.jsonl'))+[ROOT/'results/physical_consistency/trace.jsonl']:
  for line in p.read_text().splitlines():
   r=json.loads(line)
   for name,digest in r['artifact_hashes'].items():
    if sha(ROOT/name)!=digest:raise ValueError('trace artifact mismatch')
   for key,name in [('spec_hash','core/specification.json'),('code_hash','src/candidate/law.py'),('adapter_hash','adapters/operators.py'),('inference_config_hash','configs/TEST_PLAN.json')]:
    if r[key]!=sha(ROOT/name):raise ValueError('trace core mismatch '+key)
   trace_count+=1
 # Direct replay from stored fitted law parameters, no reference truth in inference.
 from adapters.operators import scalar,lift
 from src.candidate.law import rk4
 param=json.loads((ROOT/'parameters/cubic_final_300_0.json').read_text());q=np.load(ROOT/'predictions/cubic_final_300_0.npz',allow_pickle=False)
 # Raw sensor gain is1 in this named world; initial observations at saved origins.
 x=q['raw_sensor'][q['origins']];z=lift(x,2);op=scalar(*param['ab_fitted'],2);maxreplay=0.
 for t in range(1,65):
  z=rk4(op,z,.02)
  if t in (1,16,64):maxreplay=max(maxreplay,float(np.max(abs(z[:,0]-q['pred'][list(q['horizons']).index(t),0]))))
 if maxreplay!=0:raise ValueError('direct replay mismatch')
 checks.update(metric_rows=counts,max_score_difference=maxerr,trace_records=trace_count,direct_replay_max_error=maxreplay,intake=verify(ROOT),
    independent_external_replication=False,scope='same environment fresh directory / arithmetic and deterministic replay')
 return checks
if __name__=='__main__':print(json.dumps(verify_all(),indent=2))
