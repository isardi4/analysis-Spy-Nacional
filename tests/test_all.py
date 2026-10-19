import unittest,sys,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from simulate_all import states,state_lookup,run_all
class UnifiedTests(unittest.TestCase):
 def test_exact_states(self):
  ss=states();self.assertEqual(len(ss),84);self.assertEqual(len(set(ss)),84)
  look=state_lookup()
  for i,(r,w,l,d) in enumerate(ss):self.assertEqual(r,w+l+d);self.assertEqual(look[r,w,d],i)
  self.assertNotEqual(look[5,3,0],look[5,2,3]) # both nine points, different records
  self.assertEqual(ss[look[5,5,0]],(5,5,0,0));self.assertEqual(ss[look[5,3,0]],(5,3,2,0))
 def test_all_player_accounting(self):
  n=1000;z=run_all(n,24,np.array([.4,1.]),np.array([[.5,.6],[.4,.5]]),np.full((2,2),.03),state_lookup())
  e,o,opp,final,paths,hist,t,st=z
  self.assertEqual(t[:,0].sum(),n*110);self.assertEqual(t[:,1].sum(),n*8)
  self.assertEqual(e.sum(),n*770);self.assertEqual(o.sum(),n*770);self.assertEqual(opp.sum(),n*770)
  np.testing.assert_array_equal(e.sum(axis=3),o.sum(axis=3))
  np.testing.assert_array_equal(e.sum(axis=(2,3)),opp.sum(axis=2))
  np.testing.assert_array_equal(e.sum(axis=1).sum(axis=2),e.sum(axis=1).sum(axis=2).T)
  np.testing.assert_array_equal(final.sum(axis=(1,2,3)),t[:,0]);np.testing.assert_array_equal(paths.sum(axis=(1,2)),t[:,0])
  np.testing.assert_array_equal(hist.sum(axis=1),[n,n]);self.assertTrue(np.all(st<=n))
  self.assertTrue(np.all(st<=e.sum(axis=(2,3))))
  for r in range(7):self.assertEqual(e[:,[i for i,s in enumerate(states()) if s[0]==r]].sum(),n*110)
 def test_all_draw_exact_records(self):
  z=run_all(100,31,np.array([1.]),np.array([[.5]]),np.array([[1.]]),state_lookup());e=z[0]
  for i,(r,w,l,d) in enumerate(states()):self.assertEqual(int(e[:,i].sum()),11000 if w==0 and d==r else 0)
 def test_seed(self):
  args=(20,15,np.array([.3,1.]),np.full((2,2),.5),np.full((2,2),.03),state_lookup())
  for a,b in zip(run_all(*args),run_all(*args)):np.testing.assert_array_equal(a,b)
 def test_mixed_source_separation(self):
  m=np.load(ROOT/'data/processed/v2/model.npz');s=json.loads((ROOT/'data/processed/v2/sources.json').read_text())
  self.assertEqual(m['counts'].sum(),671);self.assertEqual(m['W'].shape[0],2);self.assertEqual(s['online_matches'],145)
  np.testing.assert_allclose(m['win']+m['win'].T,1);np.testing.assert_allclose(m['draw'],m['draw'].T)
if __name__=='__main__':unittest.main()
