import csv,json,sys,unittest
from io import StringIO
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from classify_decks import classify,signatures
class ClassificationTests(unittest.TestCase):
 def test_recovered_decks_have_card_evidence(self):
  audit=json.loads((ROOT/'data/processed/classified/classification_audit.json').read_text())
  self.assertEqual(len(audit),671)
  self.assertEqual(Counter(x['status'] for x in audit),dict(retained_source_label=547,recovered_card_signature=103,excluded_unknown=19,excluded_ambiguous=2))
  for row in audit:
   actual,anchors,status=classify(row)
   self.assertEqual(actual,row['classified_archetype']);self.assertEqual(anchors,row['anchors']);self.assertEqual(status,row['status'])
   if actual:self.assertNotIn('Other',actual);self.assertNotEqual(actual,'Unknown')
   if status=='recovered_card_signature':self.assertGreaterEqual(len(anchors),2)
 def test_generic_red_label_does_not_merge_different_decks(self):
  self.assertEqual(signatures({'Fiery Temper','Guttersnipe'},'Mono-Red')[0],'Red Madness')
  self.assertEqual(signatures({'Rally at the Hornburg','Goblin Bushwhacker'},'Mono-Red')[0],'Red Rally')
  self.assertIsNone(signatures({'Mountain','Lightning Bolt'},'Mono-Red')[0])
 def test_online_has_no_presence_weight_and_all_matches_retained(self):
  data=ROOT/'data/processed/classified';m=np.load(data/'model.npz');entries=list(csv.DictReader(StringIO((data/'entries.csv').read_text())))
  self.assertEqual(len(entries),650);self.assertEqual(m['counts'].sum(),650)
  self.assertFalse(any('Other' in n or n=='Unknown' for n in m['names']))
  for name,count in zip(m['names'],m['counts']):self.assertEqual(count,sum(x['archetype']==name for x in entries))
  s=json.loads((data/'sources.json').read_text());self.assertEqual(s['online_matches'],145);self.assertEqual(s['paper_matches'],1643)
  self.assertEqual(m['W'].sum()+m['D'].sum()/2,1643+145)
  np.testing.assert_allclose(m['win']+m['win'].T,1)
if __name__=='__main__':unittest.main()
