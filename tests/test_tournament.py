import unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from simulate_tournament import run_tournament,state_lookup,states
class TournamentTests(unittest.TestCase):
 def test_cut_and_playoffs_accounting(self):
  n=1000;z=run_tournament(n,201,np.array([.4,1.]),np.full((2,2),.5),np.full((2,2),.03),state_lookup())
  e,o,opp,final,paths,hist,t,st,journey,placements,playoffs=z
  self.assertEqual(t[:,0].sum(),n*110)
  for col,k in [(1,8),(4,4),(5,2),(6,1)]:self.assertEqual(t[:,col].sum(),n*k)
  self.assertEqual(journey.sum(),n*770);self.assertEqual(playoffs.sum(),n*14)
  for stage,k in [(0,4),(1,2),(2,1)]:
   self.assertEqual(playoffs[:,stage,:,1].sum(),n*k);self.assertEqual(playoffs[:,stage,:,0].sum(),n*k)
  np.testing.assert_array_equal(e.sum(axis=3),o.sum(axis=3));np.testing.assert_array_equal(e.sum(axis=(2,3)),placements.sum(axis=2))
  for deck in range(2):
   self.assertEqual(paths[deck].sum(),t[deck,0]);self.assertEqual(paths[deck,:,1:].sum(),t[deck,1])
   self.assertEqual(paths[deck,:,2:].sum(),t[deck,4]);self.assertEqual(paths[deck,:,3:].sum(),t[deck,5]);self.assertEqual(paths[deck,:,4].sum(),t[deck,6])
   for r in range(7):
    ix=[i for i,s in enumerate(states()) if s[0]==r]
    self.assertEqual(journey[deck,r].sum(),t[deck,0]);self.assertEqual(journey[deck,r,:,:,1:].sum(),t[deck,1])
    self.assertEqual(e[deck,ix].sum(),t[deck,0])
    np.testing.assert_array_equal(journey[deck,r].sum(axis=(1,2)),e[deck,ix].sum(axis=(0,2)))
    np.testing.assert_array_equal(journey[deck,r,:,:,1:].sum(axis=(1,2)),e[deck,ix,:,1].sum(axis=0))
    self.assertEqual(placements[deck,ix].sum(),t[deck,0])
 def test_symmetric_champion(self):
  n=2000;z=run_tournament(n,222,np.array([1.]),np.array([[.5]]),np.array([[0.]]),state_lookup())
  self.assertEqual(z[6][0,6],n);self.assertEqual(z[6][0,0],n*110)
 def test_all_draws_reach_playoffs(self):
  z=run_tournament(10,25,np.array([1.]),np.array([[.5]]),np.array([[1.]]),state_lookup())
  self.assertEqual(z[6][0,6],10);self.assertEqual(z[10].sum(),140)
if __name__=='__main__':unittest.main()
