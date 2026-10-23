"""Frozen scalar direct-generator benchmark; final targets generated only after freeze."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,json,time
import numpy as np
from src.common import ROOT,sha,objhash,write,append,checkpoint,now
from src.reference.worlds import nonlinear
from src.candidate.law import rk4
from adapters.operators import scalar,lift
from src.inference.fit import fit
MODELS=['F2','no_lift_quadratic','linear_drift','sparse_degree7','F0_P_legacy','persistence','training_mean']
FAMILIES=['cubic','quintic','logistic'];ORIGINS=np.array([0,16,32,48,64]);HS=[1,16,64]

def poly_step(c,x,h):
    def f(y):return np.polynomial.polynomial.polyval(y,c)
    for _ in range(4):
        dt=h/4;a=f(x);b=f(x+dt*a/2);cc=f(x+dt*b/2);d=f(x+dt*cc);x=x+dt*(a+2*b+2*cc+d)/6
    return x

def one(family,split,wid,rep,trainmean):
    tic=time.process_time();g=nonlinear(family,split,wid,rep);ab,poly,legacy=fit(g)
    measured=g['y']/g['gain'];initial=measured[ORIGINS];z=lift(initial,g['r']);op=scalar(*ab,g['r'])
    states={name:initial.copy() for name in MODELS};prev=initial.copy();pred={}
    # No future measurement is consumed inside any free rollout. Legacy lacks a prior measurement at origin0;
    # its initialization uses previous=current for ALL origins, a declared observed-memory reset.
    for t in range(1,65):
        with np.errstate(over='ignore',invalid='ignore'):
            z=rk4(op,z,g['dt']);states['F2']=z[:,0]
            for name,degree in [('no_lift_quadratic',2),('linear_drift',1),('sparse_degree7',7)]:
                states[name]=poly_step(poly[degree],states[name],g['dt'])
            cur=states['F0_P_legacy']
            for _ in range(10):
                nxt=legacy.predict(np.c_[cur,prev])[:,0];prev,cur=cur,nxt
                # Failure sink is explicit and never reused as a physical target.
                cur=np.where(np.isfinite(cur)&(np.abs(cur)<=1e6),cur,np.nan)
            states['F0_P_legacy']=cur;states['training_mean']=np.full(len(initial),trainmean)
        if t in HS:pred[t]=np.array([states[m].copy() for m in MODELS])
    param={'ab_fitted':ab.tolist(),'ab_evaluator_truth':[g['a'],g['b']],'operator':op.as_dict(),
        'poly':{str(k):v.tolist() for k,v in poly.items()},'legacy':{k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in vars(legacy).items()},
        'fit':{'reset_samples':32,'micro_time':g['hfit'],'sensor_sd':2e-6,'method':'bounded derivative matching; one fit; no hidden coefficient input'},
        'cost':{'F2_independent_parameters':2,'F2_state_dim':op.n,'F2_nonzero_terms':len(op.terms),'legacy_parameters':legacy.n_parameters,
        'linear_parameters':2,'no_lift_parameters':3,'sparse_parameters':int(np.count_nonzero(poly[7])),'fit_trials_each':1}}
    identifier=f'{family}_{split}_{wid}_{rep}';parampath=ROOT/'parameters'/f'{identifier}.json';write(parampath,param)
    arrays={'target':np.array([measured[ORIGINS+h] for h in HS]),'pred':np.array([pred[h] for h in HS]),
        'mask':np.array([g['mask'][ORIGINS+h] for h in HS]),'origins':ORIGINS,'horizons':np.array(HS),
        'raw_sensor':g['y'],'ident_x':g['ident_x'],'ident_prev':g['ident_prev'],'ident_next':g['ident_next'],
        'final_manifold':np.zeros(len(initial)) if g['r']==1 else z[:,1]-z[:,0]**g['r']}
    p=ROOT/'predictions'/f'{identifier}.npz';np.savez_compressed(p,**arrays)
    rows=[]
    for j,h in enumerate(HS):
        for k,m in enumerate(MODELS):
            pp=arrays['pred'][j,k];target=arrays['target'][j];valid=arrays['mask'][j]
            bad=~np.isfinite(pp)|(np.abs(pp)>1e6);res=pp-target
            # Nondimensional position squared; cap 1e12, with uncapped finite errors separately.
            loss=np.where(bad,1e12,np.minimum(res**2,1e12))
            rows.append(dict(family=family,split=split,world_id=wid,replicate=rep,horizon=h,model=m,
                mse=float(np.mean(loss[valid])),valid_count=int(valid.sum()),divergences=int(bad[valid].sum()),
                finite_uncapped_mse=float(np.mean(res[valid&~bad]**2)) if np.any(valid&~bad) else None,
                condition=g['kind'],prediction_file=str(p.relative_to(ROOT))))
    record={'foundation_id':'GOP_TOE_FOUNDATION_v1_0','candidate_id':'F2a','spec_hash':sha(ROOT/'core/specification.json'),
        'code_hash':sha(ROOT/'src/candidate/law.py'),'parameter_hash':sha(parampath),'adapter_hash':sha(ROOT/'adapters/operators.py'),
        'inference_config_hash':sha(ROOT/'configs/TEST_PLAN.json'),'integrator_config':{'kind':'RK4','substeps':4,'dt':g['dt'],'no_projection':True},
        'world_id':f'{family}:{split}:{wid}','split':split,'replicate':rep,'information_access_track':'accessible_reset_observations; known_sensor_calibration; per-world_few-shot_identification',
        'horizon':HS,'target_definition':'calibrated actual position readings at five fixed origins; noiseless evaluation sensor',
        'artifact_hashes':{str(p.relative_to(ROOT)):sha(p),str(parampath.relative_to(ROOT)):sha(parampath)},
        'manifold_max':float(np.max(np.abs(arrays['final_manifold']))),'parameter_abs_error':np.abs(ab-[g['a'],g['b']]).tolist(),
        'cpu_seconds':time.process_time()-tic,'classical_dimension':op.n,'shift':g['kind']}
    return rows,record

def run(split,smoke=False):
    plan=json.loads((ROOT/'configs/TEST_PLAN.json').read_text())
    if split in ('calibration','final') and not (ROOT/'configs/FREEZE.json').exists():raise RuntimeError('freeze required')
    dest=ROOT/'results/direct_generator'/f'{split}.jsonl';trace=ROOT/'results/direct_generator'/f'{split}_trace.jsonl'
    if dest.exists():raise RuntimeError('completed output exists; use saved results, do not silently repeat')
    ids=plan['ids'][split][:1] if smoke else plan['ids'][split]
    trainmean=json.loads((ROOT/'parameters/training_means.json').read_text())
    tic=time.process_time();rows=[];tr=[]
    for family in FAMILIES:
        for wid in ids:
            for rep in ([0] if smoke else [0,1]):
                rr,tt=one(family,split,wid,rep,trainmean[family]);rows+=rr;tr.append(tt)
        print(json.dumps({'family':family,'split':split,'cpu_seconds':time.process_time()-tic}),flush=True)
    # Atomic complete outputs, not interleaved parallel appends.
    dest.write_text(''.join(json.dumps(x,allow_nan=False)+'\n' for x in rows));trace.write_text(''.join(json.dumps(x)+'\n' for x in tr))
    write(ROOT/'logs'/f'{split}_run.json',{'time':now(),'cpu_seconds':time.process_time()-tic,'worlds':len(ids)*3,'realizations':len(tr),'rows':len(rows),'smoke':smoke})

def train():
    plan=json.loads((ROOT/'configs/TEST_PLAN.json').read_text());means={};ledger=[]
    for f in FAMILIES:
        ys=[]
        for wid in plan['ids']['training']:
            for rep in (0,1):
                g=nonlinear(f,'training',wid,rep);ys.extend(g['ident_next']);ledger.append({'family':f,'world_id':wid,'rep':rep,'observed_sha':objhash(g['ident_next'].tolist())})
        means[f]=float(np.mean(ys))
    write(ROOT/'parameters/training_means.json',means);write(ROOT/'logs/training_worlds.json',ledger)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('split',choices=['training','development','calibration','final']);p.add_argument('--smoke',action='store_true');a=p.parse_args()
    if a.split=='training':train()
    else:run(a.split,a.smoke)
