"""F2a: one sparse quadratic operator, continuous/discrete typed composition.
No benchmark or reference imports. No clipping/projection of a physical state.
"""
import numpy as np
from scipy.linalg import expm

class Quadratic:
    def __init__(self,n,terms,nu=0):
        self.n,self.nu,self.terms=n,nu,terms
        for i,c,js in terms:
            if not 0<=i<n or len(js)>2 or any(j<0 or j>=n+nu for j in js): raise ValueError('operator domain')
            if not np.isfinite(c) or abs(c)>1000: raise ValueError('coefficient budget')
    def __call__(self,z,u=None):
        z=np.asarray(z,float)
        if z.shape[-1]!=self.n: raise ValueError('state dimension')
        if self.nu:
            u=np.broadcast_to(np.asarray(u,float),z.shape[:-1]+(self.nu,))
            v=np.concatenate([z,u],axis=-1)
        else: v=z
        out=np.zeros_like(z)
        for i,c,js in self.terms:
            term=c
            for j in js: term=term*v[...,j]
            out[...,i]+=term
        return out
    def as_dict(self):return dict(n=self.n,nu=self.nu,terms=self.terms)

def rk4(op,z,h,u=None,substeps=4):
    z=np.asarray(z,float).copy();dt=h/substeps
    with np.errstate(over='ignore',invalid='ignore'):
        for _ in range(substeps):
            a=op(z,u);b=op(z+dt*a/2,u);c=op(z+dt*b/2,u);d=op(z+dt*c,u)
            z+=dt*(a+2*b+2*c+d)/6
    return z

def em_step(op,diffusion,z,h,noise,u=None):
    # Ito Euler-Maruyama: diffusion rows are themselves quadratic operators.
    g=np.stack([q(z) for q in diffusion],axis=-1)
    return z+h*op(z,u)+np.sqrt(h)*np.einsum('...ia,...a->...i',g,noise)

def instrument(z,H,J,G):
    y=np.asarray(H)@z
    return y,np.asarray(J)@z+np.asarray(G)@y

def fifo(buffer,signal):
    if not 1<=len(buffer)<=4:raise ValueError('delay budget')
    return np.r_[buffer[1:],signal]

def linear_moments(A,D,h):
    # Exact flow of the linear specialization of the F2 generator.
    n=len(A); V=np.block([[A,D],[np.zeros_like(A),-A.T]])*h
    E=expm(V); F=E[:n,:n];Q=E[:n,n:]@F.T
    return F,(Q+Q.T)/2

def jump_library(d):
    I=np.eye(2,dtype=complex);X=np.array([[0,1],[1,0]],complex);Y=np.array([[0,-1j],[1j,0]],complex);Z=np.diag([1.,-1.]).astype(complex)
    low=np.array([[0,1],[0,0]],complex);up=low.T
    if d==2:return [I,X,Y,Z,low,up]
    return [np.kron(a,b) for a in [I,X,Y,Z] for b in [I,X,Y,Z]]+[np.kron(a,b) for a,b in [(low,I),(up,I),(I,low),(I,up)]]

def quantum_superoperator(H,jumps,rates):
    H=np.asarray(H,complex);d=len(H)
    if d not in (2,4) or not np.allclose(H,H.conj().T):raise ValueError('Hermitian H; at most two qubits')
    I=np.eye(d);L=-1j*(np.kron(I,H)-np.kron(H.T,I))
    for J,g in zip(jumps,rates,strict=True):
        if g<0:raise ValueError('negative rate')
        J=np.asarray(J,complex)
        if not any(np.array_equal(J,q) for q in jump_library(d)):raise ValueError('jump outside frozen library')
        JJ=J.conj().T@J
        L+=g*(np.kron(J.conj(),J)-.5*np.kron(I,JJ)-.5*np.kron(JJ.T,I))
    return L

def quantum_step(rho,H,jumps,rates,h):
    S=expm(h*quantum_superoperator(H,jumps,rates))
    return (S@rho.reshape(-1,order='F')).reshape(rho.shape,order='F'),S

def branches(rho,P,eta):
    if abs(eta)>1:raise ValueError('instrument strength')
    if not np.allclose(P,P.conj().T) or not np.allclose(P@P,np.eye(len(P))):raise ValueError('Pauli involution required')
    if not any(np.array_equal(P,q) for q in jump_library(len(P))):raise ValueError('instrument outside library')
    out=[]
    for s in (-1,1):
        eig,v=np.linalg.eigh((np.eye(len(P))+s*eta*P)/2)
        M=(v*np.sqrt(np.maximum(eig,0)))@v.conj().T
        B=M@rho@M.conj().T;out.append((s,float(np.trace(B).real),B))
    return out

def choi(S,d):
    out=np.zeros((d*d,d*d),complex)
    for i in range(d):
        for j in range(d):
            E=np.zeros((d,d));E[i,j]=1
            out[i*d:(i+1)*d,j*d:(j+1)*d]=(S@E.reshape(-1,order='F')).reshape((d,d),order='F')
    return out
