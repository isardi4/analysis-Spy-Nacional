"""Recover ambiguous online playoff labels from cached primary MTGO decks.
This never contributes to paper presence. Bracket positions identify both pilots.
"""
from pathlib import Path
import csv,json
from classify_decks import signatures
ROOT=Path(__file__).resolve().parents[1]
def main():
 primary={}
 for p in (ROOT/'data/raw/online_v2').glob('*_primary.html'):
  h=p.read_text()
  if 'window.MTGO.decklists.data = ' not in h:continue
  j,_=json.JSONDecoder().raw_decode(h.split('window.MTGO.decklists.data = ',1)[1]);primary[str(j['event_id'])]=j
 rows=list(csv.DictReader((ROOT/'data/processed/online_matches_v2.csv').open()));audit=[];kept=[]
 for r in rows:
  _,eid,rnd,k=r['match_id'].split(':');j=primary[eid];players=j['brackets'][int(rnd)]['matches'][int(k)]['players'];decks={str(d['loginid']):d for d in j['decklists']}
  for q,player in zip(['a','b'],players):
   if 'Other' not in r[q] and r[q]!='Unknown':continue
   d=decks.get(str(player['loginid']));cards=set(c['card_attributes']['card_name'].split(' // ')[0] for c in d['main_deck']) if d else set()
   name,anchors=signatures(cards,r['raw_'+q])
   audit.append(dict(match_id=r['match_id'],side=q,original=r[q],raw=r['raw_'+q],classified=name,anchors=anchors,source=r['source']))
   r[q]=name or ''
  if r['a'] and r['b']:kept.append(r)
 out=ROOT/'data/processed/classified';(out/'online_classification_audit.json').write_text(json.dumps(audit,indent=2))
 with (out/'online_matches.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(kept)
 print('Online recovered labels',sum(bool(x['classified']) for x in audit),'/',len(audit),'retained matches',len(kept),'/',len(rows))
 for x in audit:
  if not x['classified']:print('Unresolved:',x['match_id'],x['raw'])
if __name__=='__main__':main()
