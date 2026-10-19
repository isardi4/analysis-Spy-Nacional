import unittest,csv,json,hashlib
from io import StringIO
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
class DataTests(unittest.TestCase):
 def test_sources_dates_coverage(self):
  es=list(csv.DictReader(StringIO((ROOT/'data/processed/events_accepted.csv').read_text())))
  entries=list(csv.DictReader(StringIO((ROOT/'data/processed/entries.csv').read_text())))
  ms=list(csv.DictReader(StringIO((ROOT/'data/processed/matches.csv').read_text())))
  self.assertEqual(len({m['match_id'] for m in ms}),len(ms))
  for e in es:
   self.assertTrue('2026-09-05'<=e['date']<='2026-10-19')
   self.assertTrue(e['venue']);self.assertTrue(e['url'].startswith('https://melee.gg/Tournament/View/'))
   self.assertEqual(int(e['players']),sum(p['event_id']==e['event_id'] for p in entries))
   self.assertEqual(int(e['matches']),sum(m['event_id']==e['event_id'] for m in ms))
 def test_model_coherence(self):
  for days in [30,45]:
   m=np.load(ROOT/f'data/processed/model{days}.npz')
   np.testing.assert_allclose(m['win']+m['win'].T,1)
   np.testing.assert_allclose(m['draw'],m['draw'].T)
   self.assertTrue(np.all((m['win']>=0)&(m['win']<=1)))
   self.assertTrue(np.all((m['draw']>=0)&(m['draw']<=1)))
   start='2026-09-20' if days==30 else '2026-09-05'
   entries=[e for e in csv.DictReader(StringIO((ROOT/'data/processed/entries.csv').read_text())) if e['date']>=start]
   self.assertEqual(int(m['counts'].sum()),len(entries))
 def test_completed_experiment(self):
  manifest=json.loads((ROOT/'results/manifest.json').read_text())
  self.assertEqual(sum(s['n'] for s in manifest['scenarios']),5000000)
  for path,digest in manifest['inputs'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
  for s in manifest['scenarios']:
   z=np.load(ROOT/f'results/{s["id"]}.npz');n=s['n'];hit=z['totals'][0]
   self.assertEqual(z['totals'][5],n);self.assertEqual(z['exposure'].sum(),7*n)
   self.assertEqual(z['records'].sum(),n);self.assertEqual(z['paths'].sum(),n)
   np.testing.assert_array_equal(z['seen'].sum(axis=2),np.broadcast_to(np.array([n-hit,hit])[:,None],z['seen'].shape[:2]))
 def test_completed_general(self):
  manifest=json.loads((ROOT/'results/general/manifest.json').read_text())
  completion=json.loads((ROOT/'results/general/completion.json').read_text())
  self.assertEqual(completion['tournaments'],manifest['planned'])
  self.assertEqual(manifest['planned'],11000000)
  for path,digest in manifest['hashes'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
  for s in manifest['scenarios']:
   z=np.load(ROOT/f'results/general/{s["id"]}.npz');n=s['n']
   self.assertEqual(z['totals'][5],n);self.assertEqual(z['exposure'].sum(),7*n)
   self.assertEqual(z['records'].sum(),n);self.assertEqual(z['paths'].sum(),n)
   self.assertEqual(z['spy_top'].sum(),n)
if __name__=='__main__':unittest.main()
