import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from simulate import pair,standings,run_batch
class EngineTests(unittest.TestCase):
 def test_no_rematches(self):
  rng=np.random.default_rng(71)
  for trial in range(100):
   h=np.full((110,7),-1,np.int64)
   for r in range(7):
    pairs=pair(rng.permutation(110),h,r)
    self.assertEqual(len(np.unique(pairs)),110)
    for a,b in pairs:
     self.assertNotEqual(a,b);self.assertNotIn(b,h[a,:r]);h[a,r]=b;h[b,r]=a
 def test_symmetric_field(self):
  r=run_batch(20000,17,np.array([1.]),np.array([[.5]]),np.array([[0.]]),0)
  self.assertLess(abs(r[-1][0]/20000-8/110),.008)
  self.assertEqual(r[-1][2],8*20000)
  self.assertEqual(r[0].sum(),7*20000)
  self.assertEqual(r[3].sum(),20000)
  self.assertEqual(r[4].sum(),20000)
  self.assertEqual(r[-1][0]+r[-1][3]+r[-1][4],20000)
 def test_reproducible(self):
  args=(100,19,np.array([.5,1.]),np.array([[.5,.65],[.35,.5]]),np.full((2,2),.03),0)
  a=run_batch(*args);b=run_batch(*args)
  for x,y in zip(a,b):np.testing.assert_array_equal(x,y)
 def test_all_draws(self):
  r=run_batch(100,11,np.array([1.]),np.array([[.5]]),np.array([[1.]]),0)
  self.assertEqual(r[3][:,0,7].sum(),100)
  self.assertEqual(r[-1][3],0)
 def test_omw_floor(self):
  pts=np.array([21,0]);h=np.array([[1]*7,[0]*7]);gw=np.array([14.,0.]);gp=np.array([14.,14.])
  omw,gwp,ogw=standings(pts,gw,gp,h)
  np.testing.assert_allclose(omw,[1/3,1]);np.testing.assert_allclose(ogw,[1/3,1])
if __name__=='__main__':unittest.main()
