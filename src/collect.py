"""Download public paper event pages; preserve raw responses and a fetch ledger."""
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import subprocess, json, csv, hashlib
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
def fetch(item):
    uid,url=item
    dest=RAW/'events'/f'{uid}.html'
    if not dest.exists():
        r=subprocess.run(['curl','-sS','-L','--fail','--retry','2','--max-time','45',url,'-o',str(dest)],capture_output=True)
        if r.returncode: return {'id':uid,'url':url,'ok':False,'error':r.stderr.decode()}
    return {'id':uid,'url':url,'ok':True,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
def main():
    (RAW/'events').mkdir(exist_ok=True)
    soup=BeautifulSoup((RAW/'events45.html').read_text(),'html.parser')
    jobs={}
    for a in soup.select('a[href]'):
        href=a['href']
        if '/meta/pauper/tournaments/' in href:
            uid=href.split('/')[-1].split('?')[0]
            jobs[uid]='https://metamages.com'+href
    ledger=list(ThreadPoolExecutor(6).map(fetch,jobs.items()))
    (RAW/'fetch_ledger.json').write_text(json.dumps(ledger,indent=2))
    print('Fetched',sum(x['ok'] for x in ledger),'/',len(ledger),flush=True)
if __name__=='__main__': main()
