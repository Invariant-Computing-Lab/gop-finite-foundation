"""Bounded observation-space surrogate; this is NOT the physical F0-G generator."""
from __future__ import annotations
import numpy as np
from scipy.linalg import cho_factor, cho_solve

class BasisRegressor:
    def __init__(self, degree=2, alpha=.1, threshold=None):
        self.degree=degree;self.alpha=alpha;self.threshold=threshold
    def _basis(self,X):
        z=(np.asarray(X)-self.xmean)/self.xscale
        z=np.clip(z,-1e50,1e50) # overflow guard, not a dynamical constraint
        blocks=[z]
        if self.degree>=2:
            blocks.append(z[:,self.pairs[:,0]]*z[:,self.pairs[:,1]])
        if self.degree>=3: blocks.append(z**3) # bounded library: coordinate cubes only
        return np.column_stack(blocks)
    def fit(self,X,Y):
        self.xmean=X.mean(0);self.xscale=np.maximum(X.std(0),1e-8)
        self.ymean=Y.mean(0);self.yscale=np.maximum(Y.std(0),1e-8)
        self.pairs=np.array([(i,j) for i in range(X.shape[1]) for j in range(i,X.shape[1])],int)
        B=self._basis(X); self.bmean=B.mean(0);self.bscale=np.maximum(B.std(0),1e-8)
        A=(B-self.bmean)/self.bscale;R=(Y-self.ymean)/self.yscale
        G=A.T@A;G.flat[::len(G)+1]+=self.alpha
        self.coef=cho_solve(cho_factor(G,check_finite=False),A.T@R,check_finite=False)
        if self.threshold is not None:
            for _ in range(4):
                for j in range(R.shape[1]):
                    active=np.abs(self.coef[:,j])>=self.threshold
                    self.coef[~active,j]=0
                    if active.any():
                        a=A[:,active];g=a.T@a;g.flat[::len(g)+1]+=self.alpha
                        self.coef[active,j]=cho_solve(cho_factor(g,check_finite=False),a.T@R[:,j],check_finite=False)
        self.n_parameters=int(self.coef.size+self.ymean.size)
        self.n_nonzero=int(np.count_nonzero(self.coef)+self.ymean.size)
        self.n_features=int(A.shape[1]);return self
    def predict(self,X):
        B=self._basis(X)
        return (((B-self.bmean)/self.bscale)@self.coef)*self.yscale+self.ymean
