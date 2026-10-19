import unittest,json,hashlib,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from simulate_tournament import states
class FinalRunTests(unittest.TestCase):
 def test_completed_shared_run(self):
  d=ROOT/'results/tournament';manifest=json.loads((d/'manifest.json').read_text());done=json.loads((d/'completion.json').read_text());z=np.load(d/'aggregate.npz')
  self.assertEqual(manifest['tournaments'],5000000);self.assertEqual(done['tournaments'],5000000)
  for p,digest in manifest['inputs'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),digest)
  t=z['totals'];self.assertEqual(t[:,0].sum(),550000000)
  for col,multiple in [(1,8),(4,4),(5,2),(6,1)]:self.assertEqual(t[:,col].sum(),5000000*multiple)
  self.assertEqual(z['exposure'].sum(),3850000000);self.assertEqual(z['playoffs'].sum(),70000000)
  self.assertEqual(z['journey'].sum(),3850000000)
  for stage,games in [(0,20000000),(1,10000000),(2,5000000)]:self.assertEqual(z['playoffs'][:,stage,:,1].sum(),games)
  self.assertTrue(np.all(np.isfinite(z['mc_se'])));self.assertTrue(np.all(z['mc_se']>=0))
 def test_paths_match_every_exact_record(self):
  z=np.load(ROOT/'results/tournament/aggregate.npz');codes=np.arange(2187);digits=np.array([[(c//(3**(6-r)))%3 for r in range(7)] for c in codes])
  masks=np.array([((digits[:,:r]==2).sum(axis=1)==w)&((digits[:,:r]==1).sum(axis=1)==d) for r,w,l,d in states()],dtype=np.int64)
  allcases=z['paths'].sum(axis=2)@masks.T;topcases=z['paths'][:,:,1:].sum(axis=2)@masks.T
  np.testing.assert_array_equal(allcases,z['exposure'].sum(axis=(2,3)))
  np.testing.assert_array_equal(topcases,z['exposure'][:,:,:,1].sum(axis=2))
  np.testing.assert_array_equal(allcases,z['state_placements'].sum(axis=2))
 def test_examples_are_in_verified_prefix(self):
  z=np.load(ROOT/'results/tournament/examples.npz');note=json.loads((ROOT/'results/tournament/examples_manifest.json').read_text());valid=z['ids'][:,:,:,0]>=0
  self.assertEqual(note['seed'],20261019);self.assertTrue(np.all(z['ids'][:,:,:,0][valid]<5000))
  self.assertTrue(np.all(z['opponents'][:,:,:,:7][valid]>=0))
  for g,stage_count in [(0,0),(1,1),(2,2),(3,3),(4,3)]:
   for k in range(z['ids'].shape[0]):
    for i in range(4):
     if z['ids'][k,g,i,0]<0:continue
     self.assertEqual(np.sum(z['opponents'][k,g,i,7:]>=0),stage_count)
if __name__=='__main__':unittest.main()
