"""Versioned explicit mappings; coefficients are data to the common operator.
These import known model structures, not a derived universal numerical law.
"""
import numpy as np
from src.candidate.law import Quadratic,rk4,instrument,fifo

def scalar(a,b,r):
    if r==1: return Quadratic(1,[(0,a,[0]),(0,-b,[0,0])])
    if r not in (2,4):raise ValueError('finite monomial grammar')
    return Quadratic(2,[(0,-a,[0]),(0,-b,[0,1]),(1,-r*a,[1]),(1,-r*b,[1,1])])

def lift(x,r):
    x=np.asarray(x,float)
    return x[...,None] if r==1 else np.stack([x,x**r],axis=-1)

def duffing(a,b,d):
    # z=(q,v,q²,qv); input u; exact on C=(z2-q²,z3-qv)=0.
    return Quadratic(4,[(0,1,[1]),(1,-a,[0]),(1,-b,[0,2]),(1,-d,[1]),(1,1,[4]),
        (2,2,[3]),(3,1,[1,1]),(3,-a,[2]),(3,-b,[2,2]),(3,-d,[3]),(3,1,[0,4])],1)

def gate(code):
    identity=[(i,1,[i]) for i in range(3)]
    maps={0:identity,1:[(0,1,[1]),(1,1,[2]),(2,1,[0])],
          2:[(0,1,[0]),(1,1,[0]),(1,1,[1]),(1,-2,[0,1]),(2,1,[2])],
          3:[(0,1,[0]),(2,1,[2])],4:[(0,1,[]),(0,-1,[0]),(1,1,[1]),(2,1,[2])]}
    return Quadratic(3,maps[int(code)])

def loop_run(cfg,steps=128,probe=0.,hybrid=False):
    from src.candidate.law import quantum_step,branches
    h=.05; delay=cfg['delay'];x=np.array([.7,-.2]);m=np.zeros(2)
    buffers=[np.zeros(delay),np.zeros(delay)];rows=[];rho=np.array([[1.,0],[0,0]],complex)
    X=np.array([[0,1],[1,0]],complex);Z=np.diag([1.,-1.]);rng=np.random.default_rng(4001)
    env=Quadratic(2,[(0,-.7,[0]),(1,-.8,[1]),(0,1,[2]),(1,1,[3])],2)
    update=Quadratic(2,[(0,.8,[0]),(0,.15,[2]),(0,.05,[4]),(1,.8,[1]),(1,.15,[3]),(1,.05,[5])],4)
    for t in range(steps):
        gain=np.array(cfg['sensor_gain']);H=np.diag(gain)
        y,measured=instrument(x,H,np.eye(2),np.diag([.01,.01])/gain)
        calibrated=y/gain;rec=np.array([b[0] for b in buffers])*cfg['connected']
        # Each endpoint decodes the other endpoint's codebook; swap is a wrong sign, not an oracle repair.
        rec*=np.array(cfg['decode'])
        m=update(m,np.r_[calibrated,rec])
        qout=0.;prob=1.;mineig=0.;trace=1.
        if hybrid:
            bs=branches(rho,Z,.35);k=int(rng.choice(2,p=[q[1] for q in bs]));qout,prob,B=bs[k]
            rho=B/prob;m[0]+=.03*qout
        action=-.3*m
        pulse=probe if t==8 else 0.
        common=.12*np.sin(.1*t) if cfg.get('common_input') else 0.
        external=np.array([pulse+common,common])
        signals=np.array(cfg['encode'])*m
        buffers=[fifo(buffers[0],signals[1]),fifo(buffers[1],signals[0])]
        xn=rk4(env,measured,h,action+external)
        if hybrid:
            rho,_=quantum_step(rho,.4*X+.1*x[0]*Z,[Z],[.1],h)
            mineig=float(np.linalg.eigvalsh(rho).min());trace=float(np.trace(rho).real)
        rows.append([t,*x,*y,*m,*action,*signals,*rec,*external,*xn,qout,prob,mineig,trace])
        x=xn
    return np.array(rows)
