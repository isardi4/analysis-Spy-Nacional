"""Complete Swiss plus seeded top8; every player and exact W/L/D state."""
import numpy as np
from numba import njit
from simulate import pair,standings

def states():
 return [(r,w,r-w-d,d) for r in range(7) for w in range(r+1) for d in range(r-w+1)]

def state_lookup():
 lookup=np.full((7,8,8),-1,np.int64)
 for s,(r,w,l,d) in enumerate(states()):lookup[r,w,d]=s
 return lookup

@njit(cache=True,nogil=True)
def run_tournament(count,seed,cdf,win,draw,lookup):
 np.random.seed(seed);K=len(cdf);N=110;S=84
 # Own archetype, exact pre-round state, opposing archetype, final top8 status.
 exposure=np.zeros((K,S,K,2),np.int64)
 outcomes=np.zeros((K,S,K,3),np.int64) # L,D,W at this round
 opp_records=np.zeros((K,S,49),np.int64) # opponent W*7+D; L inferred from round
 finals=np.zeros((K,8,8,2),np.int64)
 paths=np.zeros((K,2187,5),np.int64)
 journey=np.zeros((K,7,K,3,5),np.int64)
 state_placements=np.zeros((K,S,5),np.int64)
 playoffs=np.zeros((K,3,K,2),np.int64)
 top_hist=np.zeros((K,9),np.int64)
 state_tournaments=np.zeros((K,S),np.int64);last_seen=np.zeros((K,S),np.int64)
 totals=np.zeros((K,7),np.int64) # appearances, qualified, eliminated points, eliminated ties
 for sim in range(count):
  decks=np.empty(N,np.int64)
  for i in range(N):decks[i]=np.searchsorted(cdf,np.random.random())
  points=np.zeros(N,np.int64);wins=np.zeros(N,np.int64);ds=np.zeros(N,np.int64)
  gw=np.zeros(N);gp=np.zeros(N);hist=np.full((N,7),-1,np.int64)
  pre=np.zeros((N,7),np.int64);result=np.zeros((N,7),np.int64)
  for rnd in range(7):
   order=np.argsort(-points-np.random.random(N)*.99);pairs=pair(order,hist,rnd)
   for i in range(N):pre[i,rnd]=lookup[rnd,wins[i],ds[i]]
   for m in range(N//2):
    a=pairs[m,0];b=pairs[m,1];da=decks[a];db=decks[b];sa=pre[a,rnd];sb=pre[b,rnd]
    opp_records[da,sa,wins[b]*7+ds[b]]+=1;opp_records[db,sb,wins[a]*7+ds[a]]+=1
    hist[a,rnd]=b;hist[b,rnd]=a;u=np.random.random();v=np.random.random()
    if u<draw[da,db]:
     points[a]+=1;points[b]+=1;ds[a]+=1;ds[b]+=1;gw[a]+=1;gw[b]+=1;gp[a]+=2;gp[b]+=2;ra=1;rb=1
    else:
     awin=v<win[da,db];winner=a if awin else b;loser=b if awin else a
     points[winner]+=3;wins[winner]+=1;lg=1 if np.random.random()<.5 else 0
     gw[winner]+=2;gw[loser]+=lg;gp[a]+=2+lg;gp[b]+=2+lg;ra=2 if awin else 0;rb=0 if awin else 2
    result[a,rnd]=ra;result[b,rnd]=rb;outcomes[da,sa,db,ra]+=1;outcomes[db,sb,da,rb]+=1
  omw,gwp,ogw=standings(points,gw,gp,hist);tie=np.random.random(N);top=np.full(8,-1,np.int64)
  for i in range(N):
   for k in range(8):
    j=top[k];better=j<0
    if j>=0:
     better=(points[i]>points[j] or (points[i]==points[j] and (omw[i]>omw[j] or (omw[i]==omw[j] and (gwp[i]>gwp[j] or (gwp[i]==gwp[j] and (ogw[i]>ogw[j] or (ogw[i]==ogw[j] and tie[i]>tie[j]))))))))
    if better:
     for t in range(7,k,-1):top[t]=top[t-1]
     top[k]=i;break
  qualified=np.zeros(N,np.int64);topcounts=np.zeros(K,np.int64)
  finish=np.zeros(N,np.int64)
  # Standard seeded bracket: 1-8 / 4-5 / 2-7 / 3-6, then adjacent winners.
  bracket=np.array([top[0],top[7],top[3],top[4],top[1],top[6],top[2],top[5]])
  for i in top:finish[i]=1
  for stage in range(3):
   size=8//(2**stage);next_round=np.empty(size//2,np.int64)
   for k in range(size//2):
    a=bracket[2*k];b=bracket[2*k+1];da=decks[a];db=decks[b]
    awin=np.random.random()<win[da,db];winner=a if awin else b;loser=b if awin else a
    playoffs[da,stage,db,1 if awin else 0]+=1;playoffs[db,stage,da,0 if awin else 1]+=1
    finish[winner]+=1;next_round[k]=winner
   bracket=next_round
  for i in top:qualified[i]=1;topcounts[decks[i]]+=1
  for d in range(K):top_hist[d,topcounts[d]]+=1
  for i in range(N):
   d=decks[i];hit=qualified[i];place=finish[i];totals[d,0]+=1;totals[d,1]+=hit
   if place>=2:totals[d,4]+=1
   if place>=3:totals[d,5]+=1
   if place==4:totals[d,6]+=1
   if hit==0:
    if points[i]<points[top[7]]:totals[d,2]+=1
    else:totals[d,3]+=1
   finals[d,wins[i],ds[i],hit]+=1;code=0
   for r in range(7):
    j=hist[i,r];s=pre[i,r];exposure[d,s,decks[j],hit]+=1;code=code*3+result[i,r]
    journey[d,r,decks[j],result[i,r],place]+=1;state_placements[d,s,place]+=1
    if last_seen[d,s]!=sim+1:state_tournaments[d,s]+=1;last_seen[d,s]=sim+1
   paths[d,code,place]+=1
 return exposure,outcomes,opp_records,finals,paths,top_hist,totals,state_tournaments,journey,state_placements,playoffs
