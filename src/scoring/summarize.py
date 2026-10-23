import json
import numpy as np
from src.common import ROOT,write
FAMS=['cubic','quintic','logistic']
def read(split):return [json.loads(l) for l in (ROOT/f'results/direct_generator/{split}.jsonl').read_text().splitlines()]
def select():
 rows=read('development');out={}
 for f in FAMS:
  methods=sorted({r['model'] for r in rows if r['model']!='F2'})
  scores={m:float(np.mean([r['mse'] for r in rows if r['family']==f and r['horizon']==16 and r['model']==m])) for m in methods}
  out[f]={'primary_comparator':min(scores,key=scores.get),'development_mse_h16':scores}
 write(ROOT/'configs/COMPARATOR_SELECTION.json',out);return out

def summarize():
 rows=read('final');cal=read('calibration');chosen=json.loads((ROOT/'configs/COMPARATOR_SELECTION.json').read_text());summary=[];uncertainty=[]
 for f in FAMS:
  for m in sorted({r['model'] for r in rows}):
   for h in [1,16,64]:
    rr=[r for r in rows if r['family']==f and r['model']==m and r['horizon']==h]
    summary.append(dict(family=f,model=m,horizon=h,mse=float(np.mean([r['mse'] for r in rr])),
      divergences=sum(r['divergences'] for r in rr),valid_count=sum(r['valid_count'] for r in rr)))
  scores=[]
  for wid in range(200,212):
   err=[]
   for rep in (0,1):
    with np.load(ROOT/f'predictions/{f}_calibration_{wid}_{rep}.npz',allow_pickle=False) as z:err.extend(abs(z['pred'][:,0]-z['target']).ravel())
   scores.append(max(err))
  q=float(sorted(scores)[10]);coverage=[]
  for wid in range(300,316):
   err=[]
   for rep in (0,1):
    with np.load(ROOT/f'predictions/{f}_final_{wid}_{rep}.npz',allow_pickle=False) as z:err.extend(abs(z['pred'][:,0]-z['target']).ravel())
   coverage.append(max(err)<=q)
  uncertainty.append(dict(family=f,calibration_world_scores=scores,rank=11,n=12,nominal=.8,half_width=q,
      final_world_coverage=float(np.mean(coverage)),mean_width=2*q,coverage_by_mod4=[float(np.mean(np.array(coverage)[j::4])) for j in range(4)],
      guarantee='empirical under shift; no exchangeability guarantee'))
 comparisons=[];rng=np.random.default_rng(7851)
 for f in FAMS:
  comp=chosen[f]['primary_comparator'];delta=[]
  for wid in range(300,316):
   get=lambda m:np.mean([r['mse'] for r in rows if r['family']==f and r['world_id']==wid and r['horizon']==16 and r['model']==m])
   delta.append(get('F2')-get(comp))
  delta=np.array(delta);res=[]
  for _ in range(4000):res.append(np.mean(np.concatenate([rng.choice(delta[j::4],4,replace=True) for j in range(4)])))
  lo,hi=np.quantile(res,[.05/6,1-.05/6]);status='COMPARATIVE_SUPPORT' if hi<-.0001 else 'COMPARATIVE_FAILURE' if lo>.0001 else 'INCONCLUSIVE'
  comparisons.append(dict(family=f,comparator=comp,mean_difference=float(np.mean(delta)),approx_98_333_interval=[float(lo),float(hi)],status=status,independent_worlds=16))
 write(ROOT/'results/direct_generator/summary.json',summary);write(ROOT/'results/direct_generator/uncertainty.json',uncertainty);write(ROOT/'results/direct_generator/comparisons.json',comparisons)
 return comparisons
if __name__=='__main__':
 import sys
 print(json.dumps(select() if '--select' in sys.argv else summarize(),indent=2))
