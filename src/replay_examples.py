"""Replay a prefix of batch 0, without changing its RNG, to retain full paths.
Examples are a small nonrepresentative subset of the final five million, not new
simulations contributing to the probability denominators.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from simulate_tournament import run_tournament,state_lookup
ROOT=Path(__file__).resolve().parents[1]
def main():
 source=(ROOT/'src/simulate_tournament.py').read_text()
 source=source.replace('def run_tournament(count,seed,cdf,win,draw,lookup):','def replay(count,seed,cdf,win,draw,lookup):')
 source=source.replace('for sim in range(count):', '''examples_opp=np.full((K,5,4,10),-1,np.int64)
 examples_res=np.full((K,5,4,10),-1,np.int64)
 examples_ids=np.full((K,5,4,2),-1,np.int64)
 example_counts=np.zeros((K,5),np.int64)
 for sim in range(count):''')
 source=source.replace('for rnd in range(7):','po=np.full((N,3),-1,np.int64);pr=np.full((N,3),-1,np.int64)\n  for rnd in range(7):')
 source=source.replace('playoffs[da,stage,db,1 if awin else 0]+=1;', 'po[a,stage]=db;po[b,stage]=da;pr[a,stage]=2 if awin else 0;pr[b,stage]=0 if awin else 2\n    playoffs[da,stage,db,1 if awin else 0]+=1;')
 source=source.replace('paths[d,code,place]+=1', '''paths[d,code,place]+=1
   ec=example_counts[d,place]
   if ec<4:
    examples_ids[d,place,ec,0]=sim;examples_ids[d,place,ec,1]=i
    for r in range(7):examples_opp[d,place,ec,r]=decks[hist[i,r]];examples_res[d,place,ec,r]=result[i,r]
    for r in range(3):examples_opp[d,place,ec,r+7]=po[i,r];examples_res[d,place,ec,r+7]=pr[i,r]
    example_counts[d,place]+=1''')
 source=source.replace('return exposure,outcomes,opp_records,finals,paths,top_hist,totals,state_tournaments,journey,state_placements,playoffs', 'return exposure,outcomes,opp_records,finals,paths,top_hist,totals,state_tournaments,journey,state_placements,playoffs,examples_opp,examples_res,examples_ids')
 # numba caching cannot locate a dynamic source; this replay is a one-shot check.
 source=source.replace('cache=True','cache=False');scope={'__name__':'replay_module'};exec(compile(source,'replay_generated','exec'),scope)
 m=np.load(ROOT/'data/processed/v2/model.npz');cdf=np.cumsum(m['counts']/sum(m['counts']));cdf[-1]=1;n=5000;seed=20261019
 r=scope['replay'](n,seed,cdf,m['win'],m['draw'],state_lookup());reference=run_tournament(n,seed,cdf,m['win'],m['draw'],state_lookup())
 for a,b in zip(r[:11],reference):np.testing.assert_array_equal(a,b)
 np.savez_compressed(ROOT/'results/tournament/examples.npz',opponents=r[11],results=r[12],ids=r[13])
 note=dict(batch=0,seed=seed,replayed_prefix_tournaments=n,max_examples_per_archetype_finish=4,verified='All 11 aggregate arrays exactly match the main engine on this prefix; no additional RNG draws.',engine_sha256=hashlib.sha256((ROOT/'src/simulate_tournament.py').read_bytes()).hexdigest())
 (ROOT/'results/tournament/examples_manifest.json').write_text(json.dumps(note,indent=2));print('Verified examples replay',n,flush=True)
if __name__=='__main__':main()
