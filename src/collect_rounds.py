"""Read public standings/pairings with the same request shape as the site tables."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,urllib.parse
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw'
def fetch(job):
    kind,rid=job;dest=RAW/'rounds'/f'{kind}_{rid}.json'
    if dest.exists():
        try:
            if 'data' in json.loads(dest.read_text()):return True
        except:pass
    col='Rank' if kind=='standings' else 'TableNumber'
    params={'start':0,'length':500,'draw':1,'columns[0][data]':col,'columns[0][name]':col,'columns[0][searchable]':'true','columns[0][orderable]':'true','columns[0][search][value]':'','columns[0][search][regex]':'false','order[0][column]':0,'order[0][dir]':'asc','search[value]':'','search[regex]':'false'}
    if kind=='standings':params['roundId']=rid
    url='https://melee.gg/'+('Standing/GetRoundStandings' if kind=='standings' else 'Match/GetRoundMatches/'+rid)
    subprocess.run(['curl','-sS','--http1.1','--retry','2','--max-time','35','-H','X-Requested-With: XMLHttpRequest','--data-raw',urllib.parse.urlencode(params),url,'-o',str(dest)],capture_output=True)
    try:return 'data' in json.loads(dest.read_text())
    except:return False
if __name__=='__main__':
    (RAW/'rounds').mkdir(exist_ok=True);jobs=[]
    for e in json.load((RAW/'primary_audit.json').open()):
        rounds=e.get('rounds',[])
        if not rounds:continue
        jobs.append(('standings',rounds[0]['id']))
        for r in rounds:
            if r['name'].startswith('Round '):jobs.append(('matches',r['id']))
    for i,x in enumerate(ThreadPoolExecutor(6).map(fetch,jobs)):
        if i%25==0:print('round requests',i,'/',len(jobs),'ok',x,flush=True)
