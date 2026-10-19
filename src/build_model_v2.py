"""Paper presence remains separate from paper+online matchup outcomes."""
from pathlib import Path
from io import StringIO
import csv,json,hashlib
import numpy as np
from build_model import norm
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed';OUT=DATA/'v2'
def load(name):return list(csv.DictReader(StringIO((DATA/name).read_text())))
def normalize(raw,fallback=None):
 t=raw.lower().replace('-',' ')
 if 'grixis' in t and 'terror' in t:return 'Grixis Terror'
 if 'mardu' in t and 'metalcraft' in t:return 'Mardu Metalcraft'
 return fallback if fallback is not None else norm(raw)
def main():
 OUT.mkdir(exist_ok=True)
 entries=[p for p in load('entries.csv') if p['date']>='2026-09-20']
 # Keep taxonomy from audited paper source, correcting unambiguous color clashes.
 aliases={p['raw_archetype']:normalize(p['raw_archetype'],p['archetype']) for p in entries}
 old_to_new={} # ambiguous old categories cannot be remapped from aggregate counts
 for p in entries:p['archetype']=aliases[p['raw_archetype']]
 # Reconstruct paper matches using original Melee team/deck labels when a merged
 # label needs a split. The old normalized CSV alone cannot identify the player.
 from bs4 import BeautifulSoup
 audit=json.loads((ROOT/'data/raw/primary_audit.json').read_text());accepted={e['event_id'] for e in load('events_accepted.csv') if e['date']>='2026-09-20'}
 paper=[]
 for e in audit:
  if e['event_id'] not in accepted:continue
  rounds=[r for r in e['rounds'] if r['name'].startswith('Round ')];first=json.loads((ROOT/f"data/raw/rounds/standings_{rounds[0]['id']}.json").read_text())['data'];team={}
  for p in first:
   ds=[d for d in p.get('Decklists',[]) if d.get('Format')=='Pauper'];raw=ds[0]['DecklistName'] if ds else 'Unknown';team[p['TeamId']]=aliases.get(raw,norm(raw))
  date=next(x['date'] for x in load('events_accepted.csv') if x['event_id']==e['event_id'])
  for r in rounds:
   for m in json.loads((ROOT/f"data/raw/rounds/matches_{r['id']}.json").read_text())['data']:
    cs=m.get('Competitors',[])
    if len(cs)!=2 or not m.get('HasResult') or m.get('GhostMatch') or m.get('LossReason') is not None:continue
    a,b=cs;wa=a.get('GameWins') or 0;wb=b.get('GameWins') or 0
    if wa+wb==0 or (wa!=wb and max(wa,wb)!=2):continue
    paper.append(dict(match_id=m['Guid'],date=date,a=team[a['TeamId']],b=team[b['TeamId']],wa=wa,wb=wb,source='paper'))
 online=load('online_matches_v2.csv')
 for p in online:
  p['a']=normalize(p.get('raw_a',p['a']),p['a']);p['b']=normalize(p.get('raw_b',p['b']),p['b']);p['wa']=int(p['wa']);p['wb']=int(p['wb'])
 names=sorted({p['archetype'] for p in entries}|{p[q] for p in paper+online for q in ['a','b']});idx={n:i for i,n in enumerate(names)};K=len(names)
 counts=np.array([sum(p['archetype']==n for p in entries) for n in names]);W=np.zeros((2,K,K));D=np.zeros((2,K,K));seen=set()
 for source,ms in enumerate([paper,online]):
  for p in ms:
   key=(source,p['match_id']);assert key not in seen;seen.add(key);i=idx[p['a']];j=idx[p['b']]
   if p['wa']>p['wb']:W[source,i,j]+=1
   elif p['wb']>p['wa']:W[source,j,i]+=1
   else:D[source,i,j]+=1;D[source,j,i]+=1
 w=W.sum(axis=0);d=D.sum(axis=0);win=(w+5)/(w+w.T+10);draw=(d+.5)/(w+w.T+d+10);np.fill_diagonal(win,.5)
 for i in range(K):draw[i,i]=(d[i,i]/2+.5)/(w[i,i]+d[i,i]/2+10)
 np.savez(OUT/'model.npz',names=np.array(names),counts=counts,win=win,draw=draw,W=W,D=D)
 with (OUT/'entries.csv').open('w') as f:wr=csv.DictWriter(f,fieldnames=entries[0]);wr.writeheader();wr.writerows(entries)
 with (OUT/'paper_matches.csv').open('w') as f:wr=csv.DictWriter(f,fieldnames=paper[0]);wr.writeheader();wr.writerows(paper)
 summary=dict(paper_start='2026-09-20',end='2026-10-19',paper_events=len(accepted),paper_entries=len(entries),paper_matches=len(paper),online_events=sum(int(x['matches'])>0 for x in load('online_sources_v2.csv')),online_discovered_events=len(load('online_sources_v2.csv')),online_matches=len(online),online_scope='published_top8_playoffs_only',online_weight=1,prior_decisive_matches=10,draw_prior_mean=.05,source_note='Online playoff sample is selected; larger N does not guarantee less bias. No online deck frequency enters presence.')
 (OUT/'sources.json').write_text(json.dumps(summary,indent=2));print(summary,flush=True)
if __name__=='__main__':main()
