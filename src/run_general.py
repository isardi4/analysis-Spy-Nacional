"""Precompute every deck selector, keeping the original 5M Spy experiment intact."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np,json,hashlib,time,os
from simulate import run_batch
from run import KEYS
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed';OUT=ROOT/'results/general'
def jobspecs():
 m=np.load(DATA/'model30.npz');names=list(m['names']);jobs=[]
 for deck,name in enumerate(names):
  if m['counts'][deck]==0:continue
  for days in [30,45]:jobs.append(dict(id=f'd{deck}_w{days}',deck=deck,name=str(name),days=days,n=100000))
  obs=m['W'][deck]+m['W'][:,deck]+m['D'][deck];p=m['counts']/sum(m['counts']);score=p*(1-m['win'][deck]);targets=[]
  for j in np.argsort(-score):
   if j!=deck and names[j] not in ['Other','Unknown'] and obs[j]>=5:
    targets.append(int(j))
   if len(targets)==3:break
  for j in targets:jobs.append(dict(id=f'd{deck}_plus_{j}',deck=deck,name=str(name),days=30,n=25000,target=j,target_name=str(names[j]),delta=.05))
 return jobs

def execute(job):
 s,b,n=job;path=OUT/'batches'/f'{s["id"]}_{b:03}.npz'
 if path.exists():
  with np.load(path) as z:assert z['totals'][5]==n
  return n
 m=np.load(DATA/f'model{s["days"]}.npz');cdf=np.cumsum(m['counts']/sum(m['counts']));cdf[-1]=1;w=m['win'].copy();d=m['draw'].copy();deck=s['deck']
 seed=1092026+deck*100003+b*104729+(0 if s['days']==30 else 33)
 if 'target' in s:
  j=s['target'];w[deck,j]=min(.99,w[deck,j]+.05);w[j,deck]=1-w[deck,j]
 r=run_batch(n,seed,cdf,w,d,deck,True);tmp=path.with_suffix('.tmp.npz');np.savez_compressed(tmp,**dict(zip(KEYS,r)));os.replace(tmp,path);return n

def main():
 OUT.mkdir(exist_ok=True);(OUT/'batches').mkdir(exist_ok=True);spec=jobspecs()
 hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'model30.npz',DATA/'model45.npz',ROOT/'src/simulate.py',ROOT/'src/run_general.py']}
 manifest=dict(scenarios=spec,hashes=hashes,batch=5000,planned=sum(s['n'] for s in spec));dest=OUT/'manifest.json'
 if dest.exists():assert json.loads(dest.read_text())==manifest
 else:dest.write_text(json.dumps(manifest,indent=2))
 run_batch(1,0,np.array([1.]),np.array([[.5]]),np.array([[0.]]),0)
 start=time.time();done=0;jobs=[(s,b,5000) for s in spec for b in range(s['n']//5000)]
 print('General planned',manifest['planned'],'tournaments',len(spec),'scenarios',flush=True)
 with ThreadPoolExecutor(4) as pool:
  for f in as_completed([pool.submit(execute,j) for j in jobs]):
   done+=f.result()
   if done%500000==0:print('general',done,'/',manifest['planned'],round(time.time()-start,1),'s',flush=True)
 for s in spec:
  agg=None;rates=[]
  for p in sorted((OUT/'batches').glob(s['id']+'_*.npz')):
   with np.load(p) as z:
    vals=[z[k] for k in KEYS];rates.append(float(z['totals'][0]/z['totals'][5]))
    if agg is None:agg=[v.copy() for v in vals]
    else:
     for x,y in zip(agg,vals):x+=y
  assert agg[-1][5]==s['n'];np.savez_compressed(OUT/(s['id']+'.npz'),**dict(zip(KEYS,agg)),batch_rates=rates)
 (OUT/'completion.json').write_text(json.dumps(dict(tournaments=done,wall_seconds=time.time()-start),indent=2));print('GENERAL DONE',done,flush=True)
if __name__=='__main__':main()
