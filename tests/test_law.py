import unittest
import numpy as np
from src.candidate.law import rk4,Quadratic,branches,quantum_step
from adapters.operators import scalar,lift,duffing,gate,loop_run
from src.reference.worlds import scalar_flow,loop_reference
class LawTests(unittest.TestCase):
 def test_scalar_direct(self):
  for r in [2,4]:
   z=lift(np.array([.8]),r)[0]
   for _ in range(100):z=rk4(scalar(1,1,r),z,.01)
   self.assertLess(abs(z[0]-scalar_flow(.8,1,1,1,r)),1e-9);self.assertLess(abs(z[1]-z[0]**r),1e-8)
 def test_duffing_closure(self):
  q,v=.4,.2;z=np.array([q,v,q*q,q*v]);a,b,d,u=1,.7,.2,.1;f=duffing(a,b,d)(z,[u])
  self.assertAlmostEqual(f[2],2*q*v);self.assertAlmostEqual(f[3],v*v+q*f[1])
 def test_ito_closure(self):
  x=.3;a,b,s=1.,.7,.2;f=-a*x-b*x**3
  self.assertAlmostEqual(2*x*f+s*s,-2*a*x*x-2*b*x**4+s*s)
 def test_bits(self):
  self.assertTrue(np.array_equal(gate(2)([1,1,0]),[1,0,0]));self.assertTrue(np.array_equal(gate(3)([1,1,0]),[1,0,0]))
 def test_loop_independent(self):
  c=dict(delay=3,connected=1.,sensor_gain=[2.,.5],encode=[1.,1.],decode=[1.,1.],common_input=False)
  self.assertLess(np.max(abs(loop_run(c,steps=32)-loop_reference(c,steps=32))),1e-8)
 def test_domain(self):
  with self.assertRaises(ValueError):Quadratic(1,[(0,1,[0,0,0])])
if __name__=='__main__':unittest.main()
