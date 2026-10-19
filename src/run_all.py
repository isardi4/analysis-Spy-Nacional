"""Exactly five million complete natural-field tournaments; all 110 players."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,time,os
import numpy as np
from simulate_all import run_all,states,state_lookup
ROOT=Path(__file__).resolve().parents[1];MODEL=ROOT/'data/processed/v2/model.npz';OUT=ROOT/'results/v2'
KEYS=['exposure','outcomes','opp_records','finals','paths','top_hist','totals','state_tournaments']
def execute(job):
 b,n=job;path=OUT/'batches'/f'{b:04}.npz'
 if path.exists():
  with np.load(path) as z:assert int(z['n'])==n
  return path
 m=np.load(MODEL);cdf=np.cumsum(m['counts']/m['counts'].sum());cdf[-1]=1.;seed=20261019+b*104729
 t=time.time();rs=run_all(n,seed,cdf,m['win'],m['draw'],state_lookup());tmp=path.with_suffix('.tmp.npz')
 np.savez_compressed(tmp,**dict(zip(KEYS,rs)),n=n,seed=seed,seconds=time.time()-t);os.replace(tmp,path);return path

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--workers',type=int,default=4);a=p.parse_args()
 OUT.mkdir(exist_ok=True);(OUT/'batches').mkdir(exist_ok=True)
 m=np.load(MODEL);cdf=np.cumsum(m['counts']/sum(m['counts']));cdf[-1]=1
 t=time.time();warm=run_all(1,17,cdf,m['win'],m['draw'],state_lookup())
 if a.pilot:
  t=time.time();rs=run_all(10000,171,cdf,m['win'],m['draw'],state_lookup());print('pilot seconds',time.time()-t,'entries',rs[6][:,0].sum(),'exposures',rs[0].sum(),flush=True);return
 sources={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [MODEL,ROOT/'src/simulate_all.py',ROOT/'src/simulate.py',ROOT/'src/run_all.py']}
 manifest=dict(tournaments=5000000,players=110,rounds=7,batch_size=50000,seed=20261019,states=states(),inputs=sources,field='natural multinomial paper30; no forced seat',matchups='paper30 + published online playoffs30; source weights 1:1',pairing='score order, no rematch, local repair; not proprietary Swiss software',policy='no drops, ID or byes; draws included; BO3 scores assumed for tiebreaks')
 dest=OUT/'manifest.json'
 if dest.exists():assert json.loads(dest.read_text())==json.loads(json.dumps(manifest)),'Different inputs: use separate result directory'
 else:dest.write_text(json.dumps(manifest,indent=2))
 agg=[np.zeros_like(x) for x in warm];K=len(cdf);S=84;xx=np.zeros((K,S,K));xn=np.zeros_like(xx);nn=np.zeros((K,S));done=0;B=100;start=time.time()
 with ThreadPoolExecutor(a.workers) as pool:
  for f in as_completed([pool.submit(execute,(b,50000)) for b in range(B)]):
   with np.load(f.result()) as z:
    for i,key in enumerate(KEYS):agg[i]+=z[key]
    x=z['exposure'].sum(axis=3).astype(float);n=x.sum(axis=2);xx+=x*x;xn+=x*n[:,:,None];nn+=n*n;done+=int(z['n'])
   if done%250000==0:print(f'{done:,}/5,000,000 tournaments; {done*110:,} player paths; {time.time()-start:.1f}s',flush=True)
 e=agg[0].sum(axis=3);den=e.sum(axis=2);ratio=np.divide(e,den[:,:,None],out=np.zeros_like(xx),where=den[:,:,None]>0)
 v=B/(B-1)*(xx-2*ratio*xn+ratio*ratio*nn[:,:,None]);se=np.divide(np.sqrt(np.maximum(0,v)),den[:,:,None],out=np.zeros_like(xx),where=den[:,:,None]>0)
 assert done==5000000 and agg[0].sum()==done*770 and agg[6][:,0].sum()==done*110 and agg[6][:,1].sum()==done*8
 np.savez_compressed(OUT/'aggregate.npz',**dict(zip(KEYS,agg)),mc_se=se)
 completion=dict(tournaments=done,player_paths=done*110,matches=done*385,directed_encounters=int(agg[0].sum()),qualified=int(agg[6][:,1].sum()),wall_seconds=time.time()-start,batches=B)
 (OUT/'completion.json').write_text(json.dumps(completion,indent=2));print('DONE',completion,flush=True)
if __name__=='__main__':main()
