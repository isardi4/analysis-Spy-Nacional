from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import json, re, subprocess, hashlib, csv
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; OUT=ROOT/'data/processed'
def write(name,rows):
    if not rows:return
    with (OUT/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def getpath(guid):
    dest=RAW/'paths'/f'{guid}.json'
    if not dest.exists():
        r=subprocess.run(['curl','-sS','-L','--fail','--retry','1','--max-time','25',f'https://melee.gg/Decklist/GetTournamentViewData/{guid}','-o',str(dest)],capture_output=True)
        if r.returncode:return False
    try:return not json.loads(dest.read_text()).get('Error',True)
    except Exception:return False

def entries():
    events=[];players=[]
    for f in sorted((RAW/'events').glob('*.html')):
        soup=BeautifulSoup(f.read_text(),'html.parser');text=soup.get_text(' ',strip=True)
        heading=soup.find('h1');table=soup.find('table',{'aria-label':'Final standings'})
        if not table or not heading: continue
        date=re.search(r'([A-Z][a-z]{2} \d{1,2}, 2026)',text)
        if not date:continue
        from datetime import datetime
        d=datetime.strptime(date[1],'%b %d, %Y').date().isoformat()
        n=re.search(r'(\d+) players',text)
        if not n:continue
        # Only Melee indexed as paper; >=32 filters tiny weeklies and partial listings.
        rows=[r for r in table.select('tbody tr') if len(r.select('td'))>=4];links=[r.select('td')[1].find('a') for r in rows]
        melee=sum(bool(a and 'melee.gg/Decklist/View/' in a.get('href','')) for a in links)
        accepted=int(n[1])>=32 and melee>0 and '2026-09-05'<=d<='2026-10-19'
        events.append(dict(event_id=f.stem,name=heading.get_text(' ',strip=True),date=d,reported_entries=int(n[1]),listed_entries=len(rows),source='https://metamages.com/meta/pauper/tournaments/'+f.stem+'?platform=paper',paper_status='index_paper_not_independently_verified',accepted=accepted))
        if not accepted:continue
        for i,(r,a) in enumerate(zip(rows,links)):
            if not a:continue
            href=a.get('href','');guid=href.rsplit('/',1)[-1] if 'melee.gg/Decklist/View/' in href else ''
            cells=r.select('td');pilot=cells[2].get_text(' ',strip=True)
            players.append(dict(event_id=f.stem,date=d,player_id=hashlib.sha256((f.stem+pilot).encode()).hexdigest()[:16],pilot_source=pilot,archetype=a.get_text(' ',strip=True),guid=guid,record=cells[-1].get_text(' ',strip=True)))
    write('events.csv',events);write('entries_staging.csv',players)
    return events,players
if __name__=='__main__':
    events,players=entries();(RAW/'paths').mkdir(exist_ok=True)
    ids=sorted({p['guid'] for p in players if p['guid']})
    print('Selected events',sum(e['accepted'] for e in events),'entries',len(players),'paths',len(ids),flush=True)
    done=0;ok=0
    for x in ThreadPoolExecutor(8).map(getpath,ids):
        done+=1;ok+=x
        if done%100==0: print('paths',done,'ok',ok,flush=True)
    print('complete',done,ok,flush=True)
