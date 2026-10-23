import numpy as np
from scipy.optimize import lsq_linear
from src.inference.legacy_quadratic import BasisRegressor

def fit(g):
    x=g['ident_x'];deriv=(g['ident_next']-x)/g['hfit'];r=g['r']
    X=np.c_[x,-x*x] if r==1 else np.c_[-x,-x**(r+1)]
    ab=lsq_linear(X,deriv,bounds=(0,4),tol=1e-12).x
    # All methods receive the same accessible reset observations and fixed apparatus timing.
    # Alternatives fit drift; legacy F0-P fits the observed transition and is named separately.
    polynomial={}
    for degree in (1,2,7):
        B=np.column_stack([x**j for j in range(degree+1)])
        c=np.linalg.lstsq(B,deriv,rcond=None)[0]
        if degree==7:
            active=np.abs(c)>.02
            if active.any():c[active]=np.linalg.lstsq(B[:,active],deriv,rcond=None)[0];c[~active]=0
        polynomial[degree]=c
    legacy=BasisRegressor(2,.0001).fit(np.c_[x,g['ident_prev']],g['ident_next'][:,None])
    return ab,polynomial,legacy
