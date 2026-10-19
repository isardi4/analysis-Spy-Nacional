"""Primary MTGO playoff results: online WR evidence, never paper presence."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import json,subprocess,csv
from build_model import norm
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw/online_v2';OUT=ROOT/'data/processed'
def fetch(job):
 uid,kind,url=job;p=RAW/f'{uid}_{kind}.html'
 if not p.exists():
  r=subprocess.run(['curl','-sS','-L','--fail','--retry','1','--max-time','40',url,'-o',str(p)],capture_output=True)
  if r.returncode:raise RuntimeError(r.stderr.decode())
 return str(p)
def main():
 RAW.mkdir(exist_ok=True);s=BeautifulSoup((ROOT/'data/raw/online_events30.html').read_text(),'html.parser');jobs=[];events=[]
 for row in s.select('table tr'):
  aa=[a for a in row.select('a[href]') if '/meta/pauper/tournaments/' in a['href']];bb=[a for a in row.select('a[href]') if 'mtgo.com/decklist/' in a['href']]
  if not aa or not bb:continue
  uid=aa[0]['href'].split('/')[-1].split('?')[0]
  if uid in [e['id'] for e in events]:continue
  events.append(dict(id=uid,source=bb[0]['href']));jobs.extend([(uid,'index','https://metamages.com'+aa[0]['href']),(uid,'primary',bb[0]['href'])])
 list(ThreadPoolExecutor(6).map(fetch,jobs));matches=[];ledger=[];seen=set()
 for e in events:
  uid=e['id'];html=(RAW/f'{uid}_primary.html').read_text()
  if 'window.MTGO.decklists.data = ' not in html:
   ledger.append(dict(event_id=uid,date='',source=e['source'],matches=0,scope='excluded_primary_payload_missing'));continue
  j,_=json.JSONDecoder().raw_decode(html.split('window.MTGO.decklists.data = ',1)[1]);date=j['starttime'][:10]
  assert '2026-09-20'<=date<='2026-10-19' and j['format']=='CPAUPER'
  s=BeautifulSoup((RAW/f'{uid}_index.html').read_text(),'html.parser');aliases={};table=s.find('table')
  if table:
   for row in table.select('tbody tr'):
    cs=row.select('td')
    if len(cs)<4:continue
    a=cs[1].find('a');pilot=cs[2].get_text(' ',strip=True)
    if a:aliases[pilot]=a.get_text(' ',strip=True)
  count=0
  for rnd,bracket in enumerate(j.get('brackets',[])):
   for k,m in enumerate(bracket.get('matches',[])):
    ps=m.get('players',[])
    if len(ps)!=2:continue
    a,b=ps;an=aliases.get(a['player']);bn=aliases.get(b['player'])
    if an is None or bn is None:continue
    mid=f"mtgo:{j['event_id']}:{rnd}:{k}"
    if mid in seen:continue
    seen.add(mid);count+=1;matches.append(dict(match_id=mid,date=date,a=norm(an),b=norm(bn),raw_a=an,raw_b=bn,wa=int(a['wins']),wb=int(b['wins']),gd=0,source=e['source'],scope='published_top8_playoffs'))
  ledger.append(dict(event_id=j['event_id'],date=date,source=e['source'],matches=count,scope='published_top8_playoffs'))
 assert matches
 for name,rs in [('online_matches_v2.csv',matches),('online_sources_v2.csv',ledger)]:
  with (OUT/name).open('w') as f:w=csv.DictWriter(f,fieldnames=rs[0]);w.writeheader();w.writerows(rs)
 print('online primary',len(events),'events',len(matches),'unique playoff matches',flush=True)
if __name__=='__main__':main()
