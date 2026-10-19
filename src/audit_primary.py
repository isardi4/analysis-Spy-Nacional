from prepare import *
from bs4 import BeautifulSoup
import csv

def work(e):
    ps=list(csv.DictReader((OUT/'entries_staging.csv').open()));p=next(x for x in ps if x['event_id']==e['event_id'])
    deck=RAW/'primary'/f"{e['event_id']}_deck.html";page=RAW/'primary'/f"{e['event_id']}.html"
    if not deck.exists():subprocess.run(['curl','-sS','-L','--fail','--max-time','30','https://melee.gg/Decklist/View/'+p['guid'],'-o',str(deck)],capture_output=True)
    try:
        s=BeautifulSoup(deck.read_text(),'html.parser');a=next(a for a in s.select('a[href]') if '/Tournament/View/' in a['href']);url='https://melee.gg'+a['href']
        if not page.exists():subprocess.run(['curl','-sS','-L','--fail','--max-time','30',url,'-o',str(page)],capture_output=True)
        s=BeautifulSoup(page.read_text(),'html.parser');text=s.get_text(' ',strip=True)
        rounds=[dict(name=b.get('data-name'),id=b.get('data-id')) for b in s.select('#standings-round-selector-container button')]
        (RAW/'primary'/f"{e['event_id']}.txt").write_text(text)
        return dict(event_id=e['event_id'],url=url,rounds=rounds,text_excerpt=text[2500:5000])
    except Exception as err:return dict(event_id=e['event_id'],error=str(err))
if __name__=='__main__':
    (RAW/'primary').mkdir(exist_ok=True)
    es=[e for e in csv.DictReader((OUT/'events.csv').open()) if e['accepted']=='True']
    rows=list(ThreadPoolExecutor(6).map(work,es));(RAW/'primary_audit.json').write_text(json.dumps(rows,indent=2));print('audited',len(rows),flush=True)
