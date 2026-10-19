"""Exact-record report from one shared 5M tournament run."""
from pathlib import Path
from io import StringIO
import csv,json,html,hashlib
import numpy as np
from plotly.offline import get_plotlyjs
ROOT=Path(__file__).resolve().parents[1]
def main():
 data=ROOT/'data/processed/classified';res=ROOT/'results/classified';m=np.load(data/'model.npz');z=np.load(res/'aggregate.npz')
 manifest=json.loads((res/'manifest.json').read_text())
 for path,digest in manifest['inputs'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest, f'Input changed: {path}'
 payload={k:m[k].tolist() for k in ['names','counts','win','draw','W','D']}
 payload.update({k:z[k].tolist() for k in ['exposure','outcomes','opp_records','finals','paths','top_hist','totals','state_tournaments','mc_se','journey','state_placements','playoffs']})
 examples=np.load(res/'examples.npz');payload['examples']={k:examples[k].tolist() for k in ['opponents','results','ids']}
 payload['manifest']=json.loads((res/'manifest.json').read_text());payload['completion']=json.loads((res/'completion.json').read_text());payload['sources']=json.loads((data/'sources.json').read_text())
 assert not any('Other' in n or n=='Unknown' for n in payload['names'])
 options=''.join(f'<option value="{i}">{html.escape(n)}</option>' for i,n in enumerate(payload['names']) if payload['counts'][i]>0)
 css=(ROOT/'src/tournament.css').read_text()
 body=(ROOT/'src/templates/tournament.html').read_text().replace('OPTIONS',options)
 s=payload['sources']
 coverage=f"{s['paper_entries']} de {s['paper_entries_total']} plazas identificadas ({s['coverage']*100:.1f}%). Presencia renormalizada sobre las plazas identificadas."
 body=body.replace('COVERAGE',coverage)
 def table(headers,rows):return '<div class="tablewrap"><table><thead><tr>'+''.join('<th>'+html.escape(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
 events=list(csv.DictReader(StringIO((ROOT/'data/processed/events_accepted.csv').read_text())));online=list(csv.DictReader(StringIO((ROOT/'data/processed/online_sources_v2.csv').read_text())))
 identified=list(csv.DictReader(StringIO((data/'entries.csv').read_text())))
 sources='<h3>Presencia y matches presenciales</h3><p>Las plazas totales documentan los eventos originales; solo las identificadas alimentan la presencia del modelo.</p>'+table(['Evento','Fecha','Sede','Plazas totales','Identificadas','Fuente'],[[html.escape(e['name']),e['date'],html.escape(e['venue']),e['players'],str(sum(p['event_id']==e['event_id'] for p in identified)),f'<a href="{e["url"]}" target="_blank" rel="noreferrer">Melee ↗</a>'] for e in events if e['date']>='2026-09-20'])
 sources+='<h3>Matches online: eliminatorias publicadas</h3>'+table(['Evento','Fecha','Matches incluidos','Estado / fuente'],[[html.escape(e['event_id']),e['date'],e['matches'],f'<a href="{e["source"]}" target="_blank" rel="noreferrer">'+('MTGO ↗' if int(e['matches'])>0 else 'Excluido: sin datos primarios de partidas')+'</a>'] for e in online])
 body=body.replace('SOURCES',sources)
 js='\n'.join((ROOT/'src'/name).read_text() for name in ['matchup_stats.js','dashboard_matchups.js','dashboard_tournament.js'])
 text='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Explorador del torneo · Pauper</title><style>'+css+'</style><script>'+get_plotlyjs()+'</script></head><body><main>'+body+'</main><script>const DATA='+json.dumps(payload,separators=(',',':')).replace('</','<\\/')+';</script><script>'+js+'</script></body></html>'
 target=ROOT/'reports/metagame_explorer.html';legacy=ROOT/'reports/legacy_explorer.html'
 if not legacy.exists() and target.exists():legacy.write_bytes(target.read_bytes())
 target.write_text(text);print('Classified tournament report',len(text),'bytes',flush=True)
if __name__=='__main__':main()
