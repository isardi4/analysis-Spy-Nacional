"""Audited paper-only, date-gated datasets and reciprocal regularized matrices."""
from pathlib import Path
from bs4 import BeautifulSoup
import csv,json,re,hashlib,collections
import numpy as np
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw';OUT=ROOT/'data/processed'
def rows(path):return list(csv.DictReader(path.open()))
def write(name,rs):
    if not rs:return
    with (OUT/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def norm(s):
    s=s or 'Unknown';t=s.lower().replace('-',' ')
    rules=[('spy','Spy Combo'),('madness','Red Madness'),('elves','Elves'),('faeries','Faeries'),('monster tron','Monster Tron'),('altar tron','Altar Tron'),('flicker tron','Flicker Tron'),('ephemerate tron','Flicker Tron'),('tron','Other Tron'),('wildfire','Jund Wildfire'),('bogles','Aura Bogles'),('terror','Terror'),('delver','Mono Blue Terror'),('white weenie','White Aggro'),('white aggro','White Aggro'),('metalcraft','White Aggro'),('familiars','Familiars'),('familiar','Familiars'),('turbofog','Turbo Fog'),('turbo fog','Turbo Fog'),('cawgate','Cawgate'),('gates','Gates'),('gardens','Gardens'),('tribe','Tribe'),('inside out','Tribe'),('synth','Synthesizer'),('rally','Red Rally'),('kuldotha','Red Rally'),('affinity','Affinity'),('dimir control','Dimir Control'),('ephemerate','Ephemerate'),('glintblade','Glintblade'),('blade','Glintblade'),('ruby storm','Ruby Storm'),('cycle storm','Cycling Storm'),('cycling storm','Cycling Storm'),('poison storm','Poison Storm'),('ponza','Ponza'),('ramp','Gruul Ramp'),('monsters','Gruul Ramp'),('pestilence','Pestilence'),('stompy','Stompy'),('bully','Bully'),('zombies','Zombies'),('petitioners','Petitioners'),('dredge','Dredge'),('heroic','Heroic'),('skred','Skred'),('infect','Infect'),('walls','Walls'),('slivers','Slivers'),('kiln fiend','Hot Dogs'),('hot dogs','Hot Dogs'),('moxite','Synthesizer'),('glitters','Other Affinity'),('aristocrats','Sacrifice'),('burn','Other Burn')]
    for q,label in rules:
        if q in t:
            if label=='Faeries':return 'Dimir Faeries' if 'dimir' in t else ('Mono Blue Faeries' if 'mono' in t else 'Other Faeries')
            if label=='Terror':return 'Dimir Terror' if 'dimir' in t else 'Mono Blue Terror'
            if label=='Affinity':return 'Esper Affinity' if 'esper' in t else ('Grixis Affinity' if 'grixis' in t else 'Other Affinity')
            if label=='Red Madness':return 'Rakdos Madness' if 'rakdos' in t else label
            return label
    if s in ['Unknown','Other']:return s
    return 'Other'
def main():
    indexed=rows(OUT/'events.csv');staged=rows(OUT/'entries_staging.csv');lookup={p['guid']:norm(p['archetype']) for p in staged if p['guid']}
    events=[];entries=[];matches=[];excluded=[];aliases={};seen=set()
    for audit in json.load((RAW/'primary_audit.json').open()):
        eid=audit['event_id'];e=next(x for x in indexed if x['event_id']==eid)
        page=RAW/'primary'/f'{eid}.html'
        s=BeautifulSoup(page.read_text(),'html.parser');stamp=s.select_one('span[data-toggle="datetime"][data-value]')
        date=stamp['data-value'][:10] if stamp else ''
        venue=next((a.get_text(' ',strip=True) for a in s.select('[data-type="venue"]') if '{{' not in a.get_text()),'')
        # Require physical venue and primary date. Exclude uncertain/virtual events.
        if not venue or not ('2026-09-05'<=date<='2026-10-19'):
            excluded.append(dict(event_id=eid,reason='missing venue/date or out of window',date=date));continue
        rounds=[r for r in audit.get('rounds',[]) if r['name'].startswith('Round ')]
        if not rounds:continue
        try:
            j=json.loads((RAW/'rounds'/f"standings_{rounds[0]['id']}.json").read_text());ss=j['data']
            assert len(ss)==j['recordsTotal'] and len(ss)>=32
        except Exception:
            excluded.append(dict(event_id=eid,reason='incomplete first-round standings',date=date));continue
        participants={};event_entries=[];event_matches=[];valid=True
        for p in ss:
            ds=p.get('Decklists',[]);ds=[x for x in ds if x.get('Format')=='Pauper']
            guid=ds[0]['DecklistId'] if ds else '';raw=ds[0]['DecklistName'] if ds else 'Unknown'
            arch=lookup.get(guid,norm(raw));arch=norm(raw) if arch=='Other' else arch;aliases[raw]=arch
            tid=p['TeamId'];pid=hashlib.sha256(f'{eid}:{tid}'.encode()).hexdigest()[:16];participants[tid]=arch
            event_entries.append(dict(event_id=eid,date=date,player_id=pid,archetype=arch,raw_archetype=raw,guid=guid))
        for r in rounds:
            try:
                jj=json.loads((RAW/'rounds'/f"matches_{r['id']}.json").read_text());ms=jj['data'];assert len(ms)==jj['recordsTotal']
            except Exception:valid=False;break
            for m in ms:
                key=m['Guid']
                if key in seen:continue
                seen.add(key);cs=m.get('Competitors',[])
                if len(cs)!=2 or not m.get('HasResult') or m.get('GhostMatch') or m.get('LossReason') is not None:continue
                a,b=cs;wa=a.get('GameWins') or 0;wb=b.get('GameWins') or 0;gd=m.get('GameDraws') or 0
                # A 0-0 result (including ID) is never an observed played draw.
                if wa+wb==0:continue
                if wa!=wb and max(wa,wb)!=2:continue
                if a['TeamId'] not in participants or b['TeamId'] not in participants:
                    # A late entrant must appear in denominator too; exclude whole event.
                    valid=False;break
                event_matches.append(dict(event_id=eid,date=date,match_id=key,round=int(r['name'].split()[-1]),a=participants[a['TeamId']],b=participants[b['TeamId']],wa=wa,wb=wb,gd=gd))
            if not valid:break
        if not valid:
            excluded.append(dict(event_id=eid,reason='missing rounds or late entrant outside first round',date=date));continue
        entries+=event_entries;matches+=event_matches
        events.append(dict(event_id=eid,name=e['name'],date=date,venue=venue,players=len(ss),known_decks=sum(x['archetype']!='Unknown' for x in event_entries),matches=len(event_matches),url=audit['url'],index_url=e['source']))
    assert events and matches,'No validated events'
    write('events_accepted.csv',events);write('entries.csv',entries);write('matches.csv',matches);write('events_excluded.csv',excluded)
    write('archetype_aliases.csv',[dict(raw=k,normalized=v) for k,v in sorted(aliases.items())])
    names=sorted({p['archetype'] for p in entries});K=len(names);idx={n:i for i,n in enumerate(names)}
    summary={}
    for days,start in [(45,'2026-09-05'),(30,'2026-09-20')]:
        es=[p for p in entries if p['date']>=start];ms=[m for m in matches if m['date']>=start]
        counts=np.array([sum(p['archetype']==a for p in es) for a in names]);W=np.zeros((K,K));D=np.zeros((K,K))
        for m in ms:
            a=idx[m['a']];b=idx[m['b']]
            if m['wa']>m['wb']:W[a,b]+=1
            elif m['wb']>m['wa']:W[b,a]+=1
            else:D[a,b]+=1;D[b,a]+=1
        # Symmetric regularization: 10 virtual decisive matches at 50%;
        # draw prior 0.5/10 = 5%. ID excluded but time draws may contain IDs at 1-1.
        win=(W+5)/(W+W.T+10);draw=(D+.5)/(W+W.T+D+10)
        np.fill_diagonal(win,.5)
        for i in range(K):
            # mirror cells store one win per decisive match and two draws
            draw[i,i]=(D[i,i]/2+.5)/(W[i,i]+D[i,i]/2+10)
        np.savez(OUT/f'model{days}.npz',names=np.array(names),counts=counts,win=win,draw=draw,W=W,D=D)
        spy=idx['Spy Combo'];print(days,'days',len(es),'players',len(ms),'matches','Spy',counts[spy],flush=True)
        summary[str(days)]={'start':start,'end':'2026-10-19','events':sum(e['date']>=start for e in events),'players':len(es),'matches':len(ms),'spy_entries':int(counts[spy]),'unknown_entries':int(counts[idx['Unknown']]) if 'Unknown' in idx else 0}
    (OUT/'audit_summary.json').write_text(json.dumps(summary,indent=2))
if __name__=='__main__':main()
