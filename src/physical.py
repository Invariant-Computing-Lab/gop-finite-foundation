"""Frozen finite direct-law/physical controls, with independent targets where available."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import itertools,json,time
import numpy as np
from src.common import ROOT,sha,objhash,write,now
from src.candidate.law import Quadratic,rk4,em_step,linear_moments,quantum_step,branches,choi
from src.reference.worlds import duffing_reference,loop_reference,bit_reference,rng_for,scalar_flow
from adapters.operators import scalar,lift,duffing,loop_run,gate
from src.inference.legacy_quadratic import BasisRegressor

TRACES=[]
def save(name,arrays,params,track,target,integrator):
    p=ROOT/'predictions'/f'physical_{name}.npz';np.savez_compressed(p,**arrays)
    q=ROOT/'parameters'/f'physical_{name}.json';write(q,params)
    TRACES.append(dict(foundation_id='GOP_TOE_FOUNDATION_v1_0',candidate_id='F2a',spec_hash=sha(ROOT/'core/specification.json'),
        code_hash=sha(ROOT/'src/candidate/law.py'),adapter_hash=sha(ROOT/'adapters/operators.py'),parameter_hash=sha(q),
        inference_config_hash=sha(ROOT/'configs/TEST_PLAN.json'),integrator_config=integrator,world_id=name,split='final_fixed_control',
        information_access_track=track,horizon=[1,16,64,128],target_definition=target,
        artifact_hashes={str(p.relative_to(ROOT)):sha(p),str(q.relative_to(ROOT)):sha(q)}))

def nonlinear_controls():
    rows=[];arrays={}
    for r in (2,4):
        for h in (.1,.05,.025):
            op=scalar(1.,1.,r);z=lift(np.array([.9]),r)[0];maxC=0.
            for _ in range(round(1/h)):
                z=rk4(op,z,h,substeps=1);maxC=max(maxC,abs(z[1]-z[0]**r))
            rows.append(dict(r=r,h=h,error=float(abs(z[0]-scalar_flow(.9,1,1,1,r))),manifold=float(maxC)))
        paths=[]
        for eps in (-.1,0.,.1):
            z=np.array([.9,.9**r+eps]);path=[z.copy()]
            for _ in range(128):z=rk4(op,z,.02);path.append(z.copy())
            paths.append(path)
        arrays[f'offmanifold_r{r}']=np.array(paths)
    # Ito cubic transform: dx=(-ax-bx³)dt+sigma dW; dw=(-2aw-2bw²+sigma²)dt+2sigma*x dW.
    a,b,sigma=1.,.7,.2
    drift=Quadratic(2,[(0,-a,[0]),(0,-b,[0,1]),(1,-2*a,[1]),(1,-2*b,[1,1]),(1,sigma*sigma,[])])
    diffusion=Quadratic(2,[(0,sigma,[]),(1,2*sigma,[0])])
    ito=[];rng=np.random.default_rng(902);normal=rng.normal(size=(4096,256))
    for n in (64,128,256):
        # Nested Brownian increments, common path coupling across resolutions.
        noise=normal.reshape(4096,n,256//n).sum(axis=2)/np.sqrt(256//n)
        z=np.tile([.5,.25],(4096,1));h=.5/n
        for t in range(n):z=em_step(drift,[diffusion],z,h,noise[:,t,None])
        ito.append(dict(steps=n,manifold_rms=float(np.sqrt(np.mean((z[:,1]-z[:,0]**2)**2))),x_mean=float(z[:,0].mean()),x_variance=float(z[:,0].var())))
        arrays[f'ito_final_{n}']=z
    # A prospectively chosen mechanism-shift illustration; NOT an optimal fit over the whole F2 grammar.
    times=np.arange(129)*.02;target=scalar_flow(.95,times,1.,1.,6);z=lift(np.array([.95]),4)[0];pred=[z[0]]
    for _ in range(128):z=rk4(scalar(1.,1.,4),z,.02);pred.append(z[0])
    arrays['degree7_target']=target;arrays['fixed_quintic_prediction']=np.array(pred)
    save('lift_controls',arrays,dict(cubic_ito_drift=drift.as_dict(),diffusion=diffusion.as_dict(),coefficients=[a,b,sigma]),
        'oracle_construction; analytic predeclared counterexample','analytic deterministic flow; Ito algebra and common-noise residual',{'RK4':'substeps1 convergence / substeps4 controls','EM':'64,128,256'})
    return dict(convergence=rows,ito=ito,degree7_fixed_quintic_max_error=float(np.max(abs(target-pred))),
        analytic_obstruction='For highest lift exponent m<=4 in xdot=-x-x^7, derivative has nonzero x^(m+6), but quadratic monomials have degree<=2m. Since m+6>2m, no exact closure. Applies to autonomous identity-decoder monomial lift, no hidden physical states/instrument substitutions.',
        scientific_status='BOUNDED_INSTANCE_CONTRADICTED for universal exact closure under this grammar; known cubic/quintic conditional embeddings supported')

def mechanics():
    result=[]
    for label,a,b,d,force in [('harmonic',1.,0.,0.,0.),('duffing_forced',1.,.7,.15,.2)]:
        u=force*np.sin(np.arange(128)*.13);ref=duffing_reference(a,b,d,u,[.8,.1]);base=duffing(a,b,d)
        # Fifth coordinate integrates physical work minus dissipation, not a fictitious conserved energy.
        terms=[(i,c,[5 if j==4 else j for j in js]) for i,c,js in base.terms]
        terms += [(4,1,[1,5]),(4,-d,[1,1])]
        op=Quadratic(5,terms,1);z=np.array([.8,.1,.64,.08,0.]);path=[z.copy()]
        for force_i in u:z=rk4(op,z,.05,[force_i]);path.append(z.copy())
        path=np.array(path);E=.5*path[:,1]**2+.5*a*path[:,0]**2+.25*b*path[:,0]**4
        err=float(np.max(abs(path[:,:2]-ref)));balance=float(np.max(abs(E-E[0]-path[:,4])))
        save(label,{'prediction':path,'target':ref,'u':u,'energy':E},dict(operator=op.as_dict(),initial=path[0].tolist(),a=a,b=b,d=d),
            'oracle configured mechanical parameters; independent DOP853 target','q,v trajectory and E(t)-E(0)-integral(u*v-d*v²)',{'RK4':4,'dt':.05})
        result.append(dict(case=label,max_trajectory_error=err,work_balance_max=balance,energy_change=float(E[-1]-E[0]),
            manifold_max=float(max(np.max(abs(path[:,2]-path[:,0]**2)),np.max(abs(path[:,3]-path[:,0]*path[:,1])))),status='IMPORTED_CONSISTENCY'))
    return result

def loops():
    base={'delay':1,'connected':1.,'sensor_gain':[1.,1.],'encode':[1.,1.],'decode':[1.,1.],'common_input':False}
    configs={'connected':base,'delay3':{**base,'delay':3},'disconnected':{**base,'connected':0.},
        'swapped_codebook':{**base,'decode':[-1.,1.]},'sensor_change':{**base,'sensor_gain':[2.,.5]},
        'common_input':{**base,'connected':0.,'common_input':True}}
    rows=[]
    for name,cfg in configs.items():
        pred=loop_run(cfg);ref=loop_reference(cfg);intervention=loop_run(cfg,probe=.4)
        save('loop_'+name,{'prediction':pred,'target':ref,'intervention':intervention},cfg,
            'closed_loop_constructed_agents; no future observations; instrument/actuator are externally powered',
            'complete logged endpoint states and sensors; synthetic target0; horizon128',{'RK4':4,'h':.05,'FIFO':cfg['delay']})
        # Column2 is B world state before measurement; external probe on A at tick8.
        effect=intervention[:,2]-pred[:,2];nonzero=np.flatnonzero(abs(effect)>1e-12)
        rows.append(dict(case=name,max_reference_error=float(np.max(abs(pred-ref))),probe_B_max_effect=float(np.max(abs(effect))),
            first_B_effect_tick=int(nonzero[0]) if len(nonzero) else None,goal0_mean_world_square=float(np.mean(pred[:,1:3]**2)),
            transmission_rms=float(np.sqrt(np.mean((pred[:,11:13]-pred[:,5:7])**2))),
            transmission_metric_note='received-vs-current-memory difference includes delay; not bit error or human meaning',max_state=float(np.max(abs(pred[:,1:3])))))
    hybrid=loop_run(base,hybrid=True)
    save('loop_hybrid',{'trajectory':hybrid},base,'conditional quantum/classical construction','positivity/trace and actual outcomes; no independent oracle hybrid trajectory',{'RK4':4,'GKSL':'expm','h':.05})
    return dict(cases=rows,hybrid_min_eig=float(hybrid[:,-2].min()),hybrid_trace_error=float(np.max(abs(hybrid[:,-1]-1))),
        physical_boundary='two dissipative world coordinates; two separately updated endpoint memories; two explicit FIFOs. Work sources/reservoir dynamics outside; identity means retained state labels over 6.4 time units, not autonomous agency.')

def quantum():
    Z=np.diag([1.,-1.]).astype(complex);X=np.array([[0,1],[1,0]],complex);lower=np.array([[0,1],[0,0]],complex)
    rho=np.array([[.3,.15+.1j],[.15-.1j,.7]],complex);w,g,k=.8,.13,.4;h=.05
    pred=[rho.copy()];ref=[rho.copy()];minchoi=1.;probs=[]
    for t in range(1,129):
        rho,S=quantum_step(rho,.5*w*Z,[Z,lower],[g,k],h);pred.append(rho.copy());minchoi=min(minchoi,np.linalg.eigvalsh(choi(S,2)).min())
        tt=t*h;p11=.7*np.exp(-k*tt);off=(.15+.1j)*np.exp((-1j*w-2*g-k/2)*tt)
        ref.append(np.array([[1-p11,off],[off.conjugate(),p11]],complex))
        probs.append([x[1] for x in branches(rho,Z,.6)])
    pred=np.array(pred);ref=np.array(ref);prob=np.array(probs)
    # Two-step conditional outcome probabilities, no cloning of incompatible values.
    joint=[]
    for s,p,B in branches(pred[0],Z,.6):
        evolved,_=quantum_step(B,.2*X,[Z],[g],h)
        for ss,pp,BB in branches(evolved,X,.4):joint.append(pp)
    mixed=np.eye(2)/2;unital,_=quantum_step(mixed,.5*w*Z,[Z],[g],1.);nonunital,_=quantum_step(mixed,.5*w*Z,[lower],[k],1.)
    # Two-qubit local operation and marginal no-signalling check on Bell state.
    v=np.array([1,0,0,1],complex)/np.sqrt(2);bell=np.outer(v,v.conj());local=np.kron(lower,np.eye(2))
    out,_=quantum_step(bell,np.zeros((4,4)),[local],[k],.3)
    reduced=lambda R:np.trace(R.reshape(2,2,2,2),axis1=0,axis2=2)
    save('quantum',{'prediction':pred,'target':ref,'outcome_probabilities':prob,'joint_probabilities':np.array(joint),'local_bell_after':out},
        {'omega':w,'dephasing_rate':g,'amplitude_rate':k,'jump_extension':'lowering/raising added explicitly relative F0','initial_real':pred[0].real.tolist(),'initial_imag':pred[0].imag.tolist()},
        'oracle configured imported quantum laws','analytic density trajectory / exact conditional probabilities; strong baseline analytic channel equals reference',{'GKSL':'matrix exponential','h':h})
    return dict(max_analytic_error=float(np.max(abs(pred-ref))),min_density_eigenvalue=float(min(np.linalg.eigvalsh(q).min() for q in pred)),
        max_trace_error=float(max(abs(np.trace(q)-1) for q in pred)),min_choi_eigenvalue=float(minchoi),
        max_probability_sum_error=float(np.max(abs(prob.sum(1)-1))),joint_probability_sum=float(sum(joint)),
        unital_max_mixed_deviation=float(np.max(abs(unital-mixed))),amplitude_mixed_trace_distance=float(np.linalg.norm(nonunital-mixed,ord='nuc')/2),
        bell_no_signal_max_error=float(np.max(abs(reduced(out)-reduced(bell)))),
        status='IMPORTED_CONSISTENCY; no derived Born/GKSL law; analytic oracle baseline, no channel identification or experimental quantum data')

def discrete():
    states=np.array(list(itertools.product((0,1),repeat=3)));pred=[];target=[];ordered=0
    for s in states:
        for a,b in itertools.product(range(5),repeat=2):
            p=gate(b)(gate(a)(s));t=bit_reference(bit_reference(s,a),b);pred.append(p);target.append(t)
            ordered+=int(not np.array_equal(t,bit_reference(bit_reference(s,b),a)))
    tape=rng_for('frozen_bit_tape').integers(0,5,(128,2));longpred=[];longtarget=[]
    for s in states:
        p=s.copy();t=s.copy();pp=[p];tt=[t]
        for a,b in tape:p=gate(b)(gate(a)(p));t=bit_reference(bit_reference(t,a),b);pp.append(p);tt.append(t)
        longpred.append(pp);longtarget.append(tt)
    erased=np.array([gate(3)(s) for s in states]);retained=np.c_[erased,states[:,1]]
    # S08 uses same quadratic operator on a discrete graph, each state in its declared node neighbourhood.
    terms=[]
    for i in range(5):
        nei=[j for j in (i-1,i+1) if 0<=j<5];terms.append((i,.98-.2*len(nei),[i]))
        terms.extend((i,.2,[j]) for j in nei)
    op=Quadratic(5,terms);x=np.array([1.,0,0,0,0]);lattice=[x.copy()]
    for _ in range(8):x=op(x);lattice.append(x.copy())
    lattice=np.array(lattice);cone=max(abs(lattice[t,j]) for t in range(5) for j in range(5) if j>t)
    save('discrete',{'prediction':np.array(pred),'target':np.array(target),'long_prediction':np.array(longpred),'long_target':np.array(longtarget),
        'tape':tape,'erased':erased,'retained':retained,'lattice':lattice},
        {'gates':{str(i):gate(i).as_dict() for i in range(5)},'lattice':op.as_dict()},'known finite operator semantics; exhaustive logical states',
        'independent integer bit truth table; not learned general computation',{'discrete':'ordered polynomial maps; exact bit arithmetic'})
    return dict(ordered_pair_cases=len(pred),pair_mismatches=int(np.any(np.array(pred)!=target,axis=1).sum()),
        order_sensitive_cases=ordered,long_rollout_mismatches=int(np.any(np.array(longpred)!=longtarget,axis=-1).sum()),
        original_distinctions=8,erased_distinctions=len(np.unique(erased,axis=0)),retained_distinctions=len(np.unique(retained,axis=0)),
        max_outside_discrete_cone=float(cone),status='IMPORTED_CONSISTENCY; no Landauer heat measured, no Lorentz result')

def linear():
    rows=[];gauge_errors=[]
    for wid in range(16):
        rng=rng_for('OU_world',wid);rate=rng.uniform(.5,1.2,2);sig=np.array([.2,.25]);A=-np.diag(rate);D=np.diag(sig**2);h=.05
        F,Q=linear_moments(A,D,h);fr=np.exp(-rate*h);qr=sig**2*(1-np.exp(-2*rate*h))/(2*rate)
        H=np.array([[1.,1.]]) if wid%4==2 else np.diag([1.7,.6]) if wid%4==1 else np.eye(2)
        dim=len(H);R=.01**2*np.eye(dim);P0=np.eye(2)*.2
        for rep in (0,1):
            nr=rng_for('OU_noise',wid,rep);x=nr.multivariate_normal(np.zeros(2),P0);xx=[x.copy()]
            for t in range(128):x=fr*x+np.sqrt(qr)*nr.normal(size=2);xx.append(x.copy())
            xx=np.array(xx);y=xx@H.T+nr.normal(0,.01,(129,dim));mask=nr.random(y.shape)>.15;mask[0]=True
            # Unknown gain is represented by an equivalent observed-coordinate gauge below; no latent gain estimation claimed.
            m=np.zeros(2);P=P0.copy();filtered=[];Ps=[]
            for t in range(129):
                obs=mask[t]
                if obs.any():
                    HH=H[obs];RR=R[np.ix_(obs,obs)];S=HH@P@HH.T+RR;K=np.linalg.solve(S,HH@P).T
                    m=m+K@(y[t,obs]-HH@m);P=P-K@HH@P;P=(P+P.T)/2
                filtered.append(m.copy());Ps.append(P.copy());m=F@m;P=F@P@F.T+Q
            # Same observable history to simple baselines; train only first32 readings with valid lag pairs.
            outputs=[];targets=[];masks=[];variances=[];metas=[];simple=[]
            means=np.array([np.mean(y[:32,j][mask[:32,j]]) for j in range(dim)])
            good=mask[:30].all(1)&mask[1:31].all(1)&mask[2:32].all(1)
            X=np.c_[y[1:31],y[:30]][good];Y=y[2:32][good]
            legacy=BasisRegressor(2,.1).fit(X,Y);lin=BasisRegressor(1,.1).fit(X,Y)
            for origin in (32,48,64):
                for horizon in (1,16,64):
                    FF,QQ=linear_moments(A,D,h*horizon);mu=H@FF@filtered[origin];V=H@(FF@Ps[origin]@FF.T+QQ)@H.T+R
                    target=y[origin+horizon];valid=mask[origin+horizon];diag=np.diag(V)
                    pp=y[origin].copy();prev=y[origin-1].copy();ll=pp.copy();lp=prev.copy()
                    for _ in range(horizon):
                        with np.errstate(over='ignore',invalid='ignore'):
                            pn=legacy.predict(np.r_[pp,prev][None])[0];ln=lin.predict(np.r_[ll,lp][None])[0]
                        prev,pp=pp,pn;lp,ll=ll,ln
                    # Baseline initialization reads only available sensors, so missing origin readings are replaced by train means.
                    # Recompute those simple baselines with causal last-valid values if an initial coordinate is missing.
                    if not mask[origin].all() or not mask[origin-1].all():
                        init=[]
                        for t0 in (origin,origin-1):
                            init.append(np.array([y[np.flatnonzero(mask[:t0+1,j])[-1],j] for j in range(dim)]))
                        pp=init[0].copy();prev=init[1].copy();ll=pp.copy();lp=prev.copy()
                        for _ in range(horizon):
                            with np.errstate(over='ignore',invalid='ignore'):
                                pn=legacy.predict(np.r_[pp,prev][None])[0];ln=lin.predict(np.r_[ll,lp][None])[0]
                            prev,pp=pp,pn;lp,ll=ll,ln
                    persistence=np.array([y[np.flatnonzero(mask[:origin+1,j])[-1],j] for j in range(dim)])
                    # Analytic Kalman comparator uses independent closed diagonal transition; equality is expected.
                    f2=np.exp(-rate*h*horizon);q2=sig**2*(1-f2*f2)/(2*rate);km=H@(f2*filtered[origin])
                    outputs.append(mu);targets.append(target);masks.append(valid);variances.append(diag);simple.append([persistence,means,ll,pp,km])
                    if valid.any():
                        err=target[valid]-mu[valid];vv=V[np.ix_(valid,valid)];n=len(err)
                        nll=.5*(n*np.log(2*np.pi)+np.linalg.slogdet(vv)[1]+err@np.linalg.solve(vv,err))
                        rows.append(dict(world=wid,replicate=rep,horizon=horizon,origin=origin,valid_count=int(valid.sum()),
                            F2_mse=float(np.mean(err**2)),gaussian_joint_nll=float(nll),
                            marginal95_coverage=float(np.mean(abs(err)<=1.95996398454*np.sqrt(diag[valid]))),
                            interval_mean_width=float(np.mean(2*1.95996398454*np.sqrt(diag[valid]))),
                            max_Kalman_difference=float(np.max(abs(mu-km))),rank=int(np.linalg.matrix_rank(H))))
            # Gauge x*=2x, H*=H/2, D*=4D, P*=4P. All observation predictions unchanged.
            gauge_errors.append(float(np.max(abs((H/2)@(F@(2*filtered[32]))-H@(F@filtered[32])))))
            # Only available target readings are stored as observations; masked values are NaN, truth evaluator-only.
            observed=y.copy();observed[~mask]=np.nan
            save(f'linear_{wid}_{rep}',{'prediction':np.array(outputs),'target':np.array(targets),'mask':np.array(masks),'variance':np.array(variances),
                'baseline_predictions':np.array(simple),'observed':observed,'observation_mask':mask,'truth_evaluator_only':xx},
                {'A':A.tolist(),'D':D.tolist(),'H':H.tolist(),'R':R.tolist(),'P0':P0.tolist(),'baseline_names':['persistence','training_mean','linear','F0_P_legacy','analytic_Kalman']},
                'known-parameter observation-only Kalman filtering; sensor rank/gain prescribed; gauge nonidentifiability separate',
                'actual noisy sensor readings only when mask true',{'linear_F2':'exact matrix exponential moments','h':h})
    # Explicit rank-loss process A=-I: states with same sum remain observationally identical for all time.
    times=np.arange(129)*.05;ranknegative=np.exp(-times)*((1.+0.)-(0.+1.))
    write(ROOT/'results/physical_consistency/linear_metrics.json',rows)
    return dict(records=len(rows),valid_coordinates=sum(r['valid_count'] for r in rows),worlds=16,nested_realizations=2,
        gaussian_nll_mean=float(np.mean([r['gaussian_joint_nll'] for r in rows])),
        marginal95_coverage=float(np.average([r['marginal95_coverage'] for r in rows],weights=[r['valid_count'] for r in rows])),
        mean_interval_width=float(np.average([r['interval_mean_width'] for r in rows],weights=[r['valid_count'] for r in rows])),
        max_Kalman_difference=max(r['max_Kalman_difference'] for r in rows),gauge_max_error=max(gauge_errors),
        equal_rate_sum_sensor_negative_control=float(max(abs(ranknegative))),
        identification_status='unknown gain/scale nonidentifiable; rank-one equal-rate negative control not invertible; distinct-rate rank-one may be dynamically observable; no claim all rank loss is unidentifiable')

def main():
    if not (ROOT/'configs/FREEZE.json').exists():raise RuntimeError('freeze before controls')
    tic=time.process_time();result={}
    for name,fn in [('nonlinear',nonlinear_controls),('mechanics',mechanics),('loops',loops),('quantum',quantum),('discrete',discrete),('linear',linear)]:
        result[name]=fn();print(name,flush=True)
    write(ROOT/'results/physical_consistency/summary.json',result)
    (ROOT/'results/physical_consistency/trace.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in TRACES))
    write(ROOT/'logs/physical_run.json',{'time':now(),'cpu_seconds':time.process_time()-tic,'trace_records':len(TRACES)})
if __name__=='__main__':main()
