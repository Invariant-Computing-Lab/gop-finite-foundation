"""Independent analytic/DOP853 targets. Does not import candidate or adapters."""
import hashlib
import numpy as np
from scipy.integrate import solve_ivp

def rng_for(*parts):
    return np.random.default_rng(int.from_bytes(hashlib.sha256('|'.join(map(str,parts)).encode()).digest()[:8],'little'))

def scalar_flow(x,t,a,b,r):
    x=np.asarray(x,float)
    if r==1:return a*x*np.exp(a*t)/(a+b*x*(np.exp(a*t)-1))
    return x*np.exp(-a*t)/(1+(b/a)*x**r*(1-np.exp(-r*a*t)))**(1/r)

def nonlinear(family,split,wid,rep,steps=128):
    rng=rng_for('foundation-reference-1',family,split,wid);noise=rng_for('measurement',family,split,wid,rep)
    r={'cubic':2,'quintic':4,'logistic':1}[family];a,b=rng.uniform(.7,1.3,2)
    gain=1.7 if split=='final' and wid%4==1 else 1.
    # Accessible identification data from 32 reset preparations; micro-time h=.002.
    x=rng.uniform(.05,.95,32) if r==1 else rng.uniform(-1.,1.,32)
    hfit=.002;prev=scalar_flow(x,-hfit,a,b,r);end=scalar_flow(x,hfit,a,b,r)
    sensor_sd=2e-6
    cur=x+noise.normal(0,sensor_sd,32);nxt=end+noise.normal(0,sensor_sd,32);prv=prev+noise.normal(0,sensor_sd,32)
    initial=float(rng.uniform(.1,.9) if r==1 else rng.uniform(-.95,.95))
    if split=='final' and wid%4==2:initial=.98 if r==1 else 1.1 # preparation shift, not new mechanism
    dt=.02;truth=scalar_flow(initial,np.arange(steps+1)*dt,a,b,r)
    y=gain*truth # noiseless final calibrated position sensor, raw values retained
    return dict(a=a,b=b,r=r,gain=gain,dt=dt,hfit=hfit,ident_x=cur,ident_prev=prv,ident_next=nxt,
        y=y,truth=truth,mask=np.ones(steps+1,bool),initial=initial,kind=('sensor_transfer' if gain!=1 else 'preparation_shift' if split=='final' and wid%4==2 else 'parameter_redraw'))

def duffing_reference(a,b,d,u,x0,h=.05):
    x=np.array(x0,float);rows=[x.copy()]
    for force in u:
        sol=solve_ivp(lambda t,z:[z[1],-a*z[0]-b*z[0]**3-d*z[1]+force],(0,h),x,method='DOP853',rtol=1e-12,atol=1e-14)
        x=sol.y[:,-1];rows.append(x.copy())
    return np.array(rows)

def loop_reference(cfg,steps=128,probe=0.):
    x=np.array([.7,-.2]);m=np.zeros(2);buffers=[np.zeros(cfg['delay']),np.zeros(cfg['delay'])];rows=[]
    for t in range(steps):
        y=x*np.array(cfg['sensor_gain']);measured=x+.01*x
        rec=np.array([q[0] for q in buffers])*cfg['connected']*np.array(cfg['decode'])
        m=.8*m+.15*x+.05*rec;action=-.3*m;signals=np.array(cfg['encode'])*m
        common=.12*np.sin(.1*t) if cfg.get('common_input') else 0.
        external=np.array([(probe if t==8 else 0.)+common,common])
        u=action+external;rate=np.array([.7,.8]);xn=measured*np.exp(-rate*.05)+u/rate*(1-np.exp(-rate*.05))
        buffers=[np.r_[buffers[0][1:],signals[1]],np.r_[buffers[1][1:],signals[0]]]
        rows.append([t,*x,*y,*m,*action,*signals,*rec,*external,*xn,0.,1.,0.,1.]);x=xn
    return np.array(rows)

def bit_reference(bits,code):
    a,b,c=map(int,bits)
    if code==0:return np.array([a,b,c])
    if code==1:return np.array([b,c,a])
    if code==2:return np.array([a,a^b,c])
    if code==3:return np.array([a,0,c])
    if code==4:return np.array([1-a,b,c])
    raise ValueError(code)
