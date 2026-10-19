"""Checkpointed 5M tournament experiment. Rerun skips verified existing batches."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np,json,time,hashlib,os
from simulate import run_batch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results';DATA=ROOT/'data/processed'
KEYS=['exposure','seen','losses','records','paths','spy_top','totals']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def scenarios():
 m=np.load(DATA/'model30.npz');names=m['names'];spy=list(names).index('Spy Combo');p=m['counts']/m['counts'].sum()
 sample=m['W'][spy]+m['W'][:,spy]+m['D'][spy];score=p*(1-m['win'][spy])
 for j,n in enumerate(names):
  if n in ['Other','Unknown','Spy Combo'] or sample[j]<5 or m['win'][spy,j]>=.5:score[j]=-1
 targets=list(np.argsort(-score)[:3]);assert all(score[j]>0 for j in targets)
 sc=[dict(id='central30',n=1500000,days=30,focal=True),dict(id='window45',n=500000,days=45,focal=True),dict(id='parameters30',n=500000,days=30,focal=True,posterior=True),dict(id='natural30',n=1000000,days=30,focal=False)]
 for j in targets:
  for delta in [.02,.05]:sc.append(dict(id=f'improve_{j}_{int(delta*100)}',n=250000,days=30,focal=True,target=str(names[j]),target_index=int(j),delta=delta))
 return sc

def execute(job):
 scenario,batch,n=job;sid=scenario['id'];path=OUT/'batches'/f'{sid}_{batch:04}.npz'
 if path.exists():
  with np.load(path) as z:
   assert int(z['totals'][5])==n
  return sid,n,None
 m=np.load(DATA/f"model{scenario['days']}.npz");names=m['names'];spy=list(names).index('Spy Combo')
 counts=m['counts'].copy();win=m['win'].copy();draw=m['draw'].copy()
 # Common seeds for central and improvement scenarios. Diverging pairings are
 # recomputed; common RNG is only partial coupling, never fixed opponents.
 code=0 if sid=='central30' or sid.startswith('improve_') else int(hashlib.sha256(sid.encode()).hexdigest()[:6],16)
 seed=(20261019+batch*104729+code)%2147483647
 if scenario.get('posterior'):
  rng=np.random.default_rng(seed);counts=rng.dirichlet(counts+.5)
  W=m['W'];D=m['D'];K=len(names)
  for i in range(K):
   for j in range(i+1,K):
    win[i,j]=rng.beta(W[i,j]+5,W[j,i]+5);win[j,i]=1-win[i,j]
    draw[i,j]=draw[j,i]=rng.beta(D[i,j]+.5,W[i,j]+W[j,i]+9.5)
 if 'target_index' in scenario:
  j=scenario['target_index'];win[spy,j]=min(.99,win[spy,j]+scenario['delta']);win[j,spy]=1-win[spy,j]
 cdf=np.cumsum(counts/counts.sum());cdf[-1]=1
 t=time.time();r=run_batch(n,seed,cdf,win,draw,spy,scenario['focal'])
 tmp=path.with_suffix('.tmp.npz');np.savez_compressed(tmp,**dict(zip(KEYS,r)),seed=seed,seconds=time.time()-t);os.replace(tmp,path)
 return sid,n,r[-1][0]/n

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4);parser.add_argument('--pilot',action='store_true');args=parser.parse_args()
 OUT.mkdir(exist_ok=True);(OUT/'batches').mkdir(exist_ok=True)
 sc=scenarios();sources={str(p.relative_to(ROOT)):sha(p) for p in DATA.glob('model*.npz')}
 sources['src/simulate.py']=sha(ROOT/'src/simulate.py')
 manifest=dict(total_planned=sum(s['n'] for s in sc),scenarios=sc,inputs=sources,seed=20261019,batch_size=5000,engine='Swiss approximation: no ID/drops/byes; BO3 assumed score; OMW/GW/OGW; 110 seats, 7 rounds',numpy=np.__version__)
 if args.pilot:
  t=time.time();result=execute((dict(sc[0],id='pilot'),0,10000));print('pilot',result,'seconds',time.time()-t,flush=True);return
 dest=OUT/'manifest.json'
 if dest.exists():assert json.loads(dest.read_text())==manifest,'Inputs changed: archive old results before rerunning'
 else:dest.write_text(json.dumps(manifest,indent=2))
 jobs=[]
 for s in sc:
  for b in range(s['n']//5000):jobs.append((s,b,5000))
 # Compile before threads launch; each batch resets its thread-local random seed.
 execute((dict(sc[0],id='warmup'),0,1))
 start=time.time();done=0
 with ThreadPoolExecutor(args.workers) as pool:
  for f in as_completed([pool.submit(execute,j) for j in jobs]):
   sid,n,p=f.result();done+=n
   if done%100000==0:print(f'{done:,}/{manifest["total_planned"]:,} completed; {time.time()-start:.1f}s',flush=True)
 for s in sc:
  paths=sorted((OUT/'batches').glob(s['id']+'_*.npz'));agg=None;rates=[]
  for p in paths:
   with np.load(p) as z:
    values=[z[k] for k in KEYS];rates.append(float(z['totals'][0]/z['totals'][5]))
    if agg is None:agg=[x.copy() for x in values]
    else:
     for x,y in zip(agg,values):x+=y
  assert int(agg[-1][5])==s['n']
  np.savez_compressed(OUT/(s['id']+'.npz'),**dict(zip(KEYS,agg)),batch_rates=rates)
 (OUT/'completion.json').write_text(json.dumps(dict(tournaments=sum(s['n'] for s in sc),wall_seconds=time.time()-start,input_hashes=sources),indent=2))
 print('DONE',sum(s['n'] for s in sc),flush=True)
if __name__=='__main__':main()
