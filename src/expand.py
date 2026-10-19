"""Abandoned probe: this endpoint exposes only top8, so it accepts no events.
Retained for audit only. Use collect_rounds.py and build_model.py instead.
"""
from prepare import *
import csv
if __name__=='__main__':
    staged=list(csv.DictReader((OUT/'entries_staging.csv').open())); events=list(csv.DictReader((OUT/'events.csv').open()))
    allrows=[]; audit=[]
    for e in events:
        if e['accepted']!='True':continue
        ps=[p for p in staged if p['event_id']==e['event_id']]
        best=[]
        for p in ps:
            try:
                j=json.loads(json.loads((RAW/'paths'/f"{p['guid']}.json").read_text())['Json'])
                if len(j['Standings'])>len(best):best=j['Standings']
            except Exception:pass
        n=int(e['reported_entries']);coverage=len(best)/n
        # Complete primary standings only. Missing archetypes retained as Unknown.
        accepted=len(best)>=n
        audit.append(dict(event_id=e['event_id'],name=e['name'],date=e['date'],reported_entries=n,primary_standings=len(best),accepted=accepted,source=e['source']))
        if not accepted:continue
        for s in best:
            user=s.get('PlayerUsername') or s['PlayerName'];g=s.get('DecklistGuid') or ''
            indexed=next((p['archetype'] for p in ps if p['guid']==g),'') if g else ''
            allrows.append(dict(event_id=e['event_id'],date=e['date'],player_id=hashlib.sha256((e['event_id']+user).encode()).hexdigest()[:16],pilot_source=user,raw_archetype=s.get('DecklistName') or 'Unknown',indexed_archetype=indexed,guid=g,record=s.get('MatchRecord','')))
    write('coverage.csv',audit);write('entries_primary.csv',allrows)
    ids=sorted({p['guid'] for p in allrows if p['guid']})
    print('Complete events',sum(a['accepted'] for a in audit),'players',len(allrows),'paths',len(ids),flush=True)
    for i,ok in enumerate(ThreadPoolExecutor(8).map(getpath,ids)):
        if i%100==0:print('paths processed',i,flush=True)
