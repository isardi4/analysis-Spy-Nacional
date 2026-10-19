"""Swiss approximation: score groups, no rematches, OMW/GW/OGW standings.
No drops, earned byes, intentional draws or skill model. Exactly 110 seats.
"""
import numpy as np
from numba import njit

@njit(cache=True)
def pair(order, history, rnd):
    # Greedy nearest-score matching, repair a blocked last pair by swapping one
    # previously assigned pair. With <=6 forbidden opponents and 110 seats a
    # compatible repair exists; fail explicitly instead of accepting a rematch.
    n=len(order); pool=order.copy(); pairs=np.empty((n//2,2),np.int64)
    for k in range(n//2):
        pos=2*k;a=pool[pos];chosen=-1
        for j in range(pos+1,n):
            b=pool[j];ok=True
            for r in range(rnd):
                if history[a,r]==b:ok=False;break
            if ok:chosen=j;break
        if chosen>=0:
            b=pool[chosen];pool[chosen]=pool[pos+1];pool[pos+1]=b
            pairs[k,0]=a;pairs[k,1]=b
        else:
            b=pool[pos+1];fixed=False
            for t in range(k-1,-1,-1):
                c=pairs[t,0];d=pairs[t,1]
                for swap in range(2):
                    x=c if swap==0 else d;y=d if swap==0 else c
                    ok=True
                    for r in range(rnd):
                        if history[a,r]==x or history[b,r]==y:ok=False;break
                    if ok:
                        pairs[t,0]=a;pairs[t,1]=x;pairs[k,0]=b;pairs[k,1]=y
                        fixed=True;break
                if fixed:break
            if not fixed:raise ValueError('Pair repair failed')
    return pairs

@njit(cache=True)
def standings(points,gw,gp,hist):
    n=len(points);mwp=np.maximum(points/21.,1./3.);gwp=np.maximum(gw/gp,1./3.)
    omw=np.zeros(n);ogw=np.zeros(n)
    for i in range(n):
        for r in range(7):
            omw[i]+=mwp[hist[i,r]]/7.;ogw[i]+=gwp[hist[i,r]]/7.
    # Integer points first; quantization only resolves numerical equality.
    # Selection below uses explicit lexicographic comparisons.
    return omw,gwp,ogw

@njit(cache=True, nogil=True)
def run_batch(count,seed,cdf,win,draw,spy,focal=True):
    np.random.seed(seed);K=len(cdf);N=110
    # outcome 0=miss 1=top8, round, prior points, opponent
    exposure=np.zeros((2,7,22,K),np.int64)
    seen=np.zeros((2,K,8),np.int64)
    losses=np.zeros((2,K),np.int64)
    records=np.zeros((2,8,8),np.int64)
    paths=np.zeros((2,2187),np.int64)
    spy_top=np.zeros(9,np.int64)
    totals=np.zeros(6,np.int64) # focal top, spy entries, spy qualified, point miss, tie miss, tournaments
    for sim in range(count):
        decks=np.empty(N,np.int64)
        for i in range(N):decks[i]=np.searchsorted(cdf,np.random.random())
        if focal:decks[0]=spy
        points=np.zeros(N,np.int64);wins=np.zeros(N,np.int64);ds=np.zeros(N,np.int64)
        gw=np.zeros(N);gp=np.zeros(N);hist=np.full((N,7),-1,np.int64)
        before=np.zeros(7,np.int64);opp=np.zeros(7,np.int64);res=np.zeros(7,np.int64)
        for rnd in range(7):
            order=np.argsort(-points-np.random.random(N)*.99)
            pairs=pair(order,hist,rnd)
            before[rnd]=points[0]
            for m in range(N//2):
                a=pairs[m,0];b=pairs[m,1];da=decks[a];db=decks[b]
                hist[a,rnd]=b;hist[b,rnd]=a
                u=np.random.random();v=np.random.random()
                if u<draw[da,db]:
                    points[a]+=1;points[b]+=1;ds[a]+=1;ds[b]+=1
                    gw[a]+=1;gw[b]+=1;gp[a]+=2;gp[b]+=2;ra=1;rb=1
                else:
                    awin=v<win[da,db]
                    winner=a if awin else b;loser=b if awin else a
                    points[winner]+=3;wins[winner]+=1
                    # BO3 score assumption: half 2-0 and half 2-1.
                    lg=1 if np.random.random()<.5 else 0
                    gw[winner]+=2;gw[loser]+=lg;gp[a]+=2+lg;gp[b]+=2+lg
                    ra=2 if awin else 0;rb=0 if awin else 2
                if a==0:opp[rnd]=db;res[rnd]=ra
                elif b==0:opp[rnd]=da;res[rnd]=rb
        omw,gwp,ogw=standings(points,gw,gp,hist)
        # Random final ties, lexicographic top8 insertion.
        tie=np.random.random(N);top=np.full(8,-1,np.int64)
        for i in range(N):
            for k in range(8):
                j=top[k];better=j<0
                if j>=0:
                    better=(points[i]>points[j] or (points[i]==points[j] and (omw[i]>omw[j] or (omw[i]==omw[j] and (gwp[i]>gwp[j] or (gwp[i]==gwp[j] and (ogw[i]>ogw[j] or (ogw[i]==ogw[j] and tie[i]>tie[j]))))))))
                if better:
                    for t in range(7,k,-1):top[t]=top[t-1]
                    top[k]=i;break
        hit=0;st=0
        for k in range(8):
            if top[k]==0:hit=1
            if decks[top[k]]==spy:st+=1
        totals[0]+=hit;totals[1]+=np.sum(decks==spy);totals[2]+=st;totals[5]+=1;spy_top[st]+=1
        if hit==0:
            if points[0]<points[top[7]]:totals[3]+=1
            else:totals[4]+=1
        records[hit,wins[0],ds[0]]+=1
        visits=np.zeros(K,np.int64);code=0
        for r in range(7):
            exposure[hit,r,before[r],opp[r]]+=1;visits[opp[r]]+=1
            if res[r]==0:losses[hit,opp[r]]+=1
            code=code*3+res[r]
        paths[hit,code]+=1
        for d in range(K):seen[hit,d,visits[d]]+=1
    return exposure,seen,losses,records,paths,spy_top,totals
