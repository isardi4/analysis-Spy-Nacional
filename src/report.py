"""Generate an offline, self-contained analysis with interactive Plotly figures."""
from pathlib import Path
import json,csv,html,math
import numpy as np
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/processed';RES=ROOT/'results'
def records(name):return list(csv.DictReader((DATA/name).open()))
def fmt(x):return f'{x:,.0f}'.replace(',','.')
def pct(x):return f'{100*x:.2f}%'.replace('.',',')
def wilson(k,n):
 if not n:return (float('nan'),float('nan'))
 p=k/n;z=1.96;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return mid-half,mid+half
def table(headers,rs):
 return '<div class="tablewrap"><table><thead><tr>'+''.join('<th>'+html.escape(str(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in row)+'</tr>' for row in rs)+'</tbody></table></div>'
def main():
 completion=json.loads((RES/'completion.json').read_text());manifest=json.loads((RES/'manifest.json').read_text());audit=json.loads((DATA/'audit_summary.json').read_text())
 m=np.load(DATA/'model30.npz');m45=np.load(DATA/'model45.npz');names=list(m['names']);K=len(names);spy=names.index('Spy Combo');p=m['counts']/sum(m['counts']);p45=m45['counts']/sum(m45['counts'])
 z=np.load(RES/'central30.npz');nat=np.load(RES/'natural30.npz');tot=z['totals'];N=int(tot[5]);hits=int(tot[0]);rate=hits/N
 exposure=z['exposure'];seen=z['seen'];losses=z['losses'];counts=m['counts'];W=m['W'];D=m['D'];draw=m['draw'];win=m['win'];nmatch=W+W.T+D
 pieces=[];charts=[]
 def paragraph(s):pieces.append('<p>'+s+'</p>')
 def heading(s):pieces.append('<h2>'+s+'</h2>')
 def chart(fig,title):
  fig.update_layout(template='plotly_white',font=dict(family='Arial',color='#24333f'),paper_bgcolor='#fffdf8',plot_bgcolor='#fffdf8',margin=dict(l=45,r=25,t=70,b=80),title=dict(text=title,font=dict(size=18)),height=470)
  fig.update_xaxes(automargin=True);fig.update_yaxes(automargin=True)
  pieces.append(fig.to_html(full_html=False,include_plotlyjs=False,config={'responsive':True,'displaylogo':False}));charts.append(title)
 pieces.append('<div class="eyebrow">LABORATORIO · PAUPER EN PAPEL</div><h1>Los caminos de Spy<br>al top 8</h1><p class="lead">110 jugadores · 7 rondas · 5 millones de torneos simulados</p>')
 paragraph('Corte de datos: <b>19 de octubre de 2026</b>. Principal: 20/09–19/10 (30 días inclusivos). Comparación: 05/09–19/10 (45 días inclusivos). Formato y arquetipo de trabajo: Pauper / Balustrade Spy; lista de 75 y región objetivo todavía no confirmadas.')
 lo,hi=wilson(hits,N)
 pieces.append('<div class="cards">'+''.join(f'<div class="card"><span>{a}</span><strong>{b}</strong><small>{c}</small></div>' for a,b,c in [('Tu plaza de Spy · top 8',pct(rate),f'{fmt(hits)} de {fmt(N)} torneos principales'),('Al menos un Spy en top 8',pct(1-nat['spy_top'][0]/nat['totals'][5]),'Field natural · 1.000.000 de torneos'),('Muestra presencial · 30 días',fmt(audit['30']['players']),f"{audit['30']['events']} eventos · {fmt(audit['30']['matches'])} matches"),('Precisión del azar · principal',f'±{(hi-lo)*50:.3f} pp','IC 95% Monte Carlo; no incluye error de datos')])+'</div>')
 pieces.append('<div class="notice"><b>Lectura correcta.</b> Estas son probabilidades condicionadas a una muestra y a un modelo aproximado de suizo. No son una predicción específica del Nacional: faltan la región y tu lista, hay cruces con pocas observaciones, y no se simulan empates intencionales, drops, diferencias de habilidad ni byes. Los cinco millones se distribuyen entre escenarios; el escenario principal tiene 1,5 millones.</div>')
 heading('Qué datos entraron')
 paragraph('Se descubrieron eventos con un índice filtrado como papel y se contrastaron con las páginas públicas de Melee. Se exige fecha primaria dentro de ventana, sede física publicada, al menos 32 participantes en la tabla de primera ronda, paginación completa y tablas de todas las rondas suizas. Se excluyen eliminatorias, byes, resultados 0-0 (incluidos ID), concesiones marcadas y resultados no terminados a dos juegos ganados. Los empates jugados con juegos registrados sí entran; un ID pactado después de jugar puede no ser distinguible. Se omiten eventos sin sede verificable. La tabla de primera ronda define el field; los eventos con participantes tardíos no cubiertos se excluyen.')
 paragraph(f"Ventana de 45 días: {audit['45']['events']} eventos, {fmt(audit['45']['players'])} plazas, {fmt(audit['45']['matches'])} matches y {audit['45']['spy_entries']} plazas de Spy. Ventana de 30 días: {audit['30']['events']} eventos y {audit['30']['spy_entries']} plazas de Spy. Son participaciones en eventos, no necesariamente personas únicas. Se pondera por participación; no hay ponderación argentina ni corrección por jugadores recurrentes.")
 order=np.argsort(-counts);show=order[:18]
 fig=go.Figure()
 fig.add_bar(name='30 días',x=[names[i] for i in show],y=p[show]*100,customdata=counts[show],hovertemplate='%{x}: %{y:.2f}% · %{customdata} plazas<extra>30 días</extra>',marker_color='#176d81')
 fig.add_bar(name='45 días',x=[names[i] for i in show],y=p45[show]*100,marker_color='#d3a04a')
 chart(fig,'Presencia observada · denominador: field completo de eventos aceptados')
 paragraph(f"Spy ocupa {pct(p[spy])} del field de 30 días: {110*p[spy]:.2f} plazas esperadas si se sortean los 110 jugadores. Si reservás tu plaza, el total esperado es {1+109*p[spy]:.2f}. No se redondean porcentajes para armar el field: se sortean conteos enteros multinomiales.")
 other=names.index('Other');unknown=names.index('Unknown')
 paragraph(f"Cobertura de etiquetas: Other = {pct(p[other])}; Unknown = {pct(p[unknown])}. Other reúne etiquetas insuficientes y mazos minoritarios; Unknown indica falta de lista. Estas categorías se conservan y su comportamiento se estima desde sus matches disponibles. La agregación puede ocultar diferencias relevantes. Los alias están exportados para revisar fusiones como las variantes de Ephemerate o de Gates.")
 heading('Qué tan buenos son los matchups de Spy')
 rows=[]
 for j in order:
  w=int(W[spy,j]);l=int(W[j,spy]);d=int(D[spy,j]);n=w+l+d
  if j==spy:w=int(W[spy,j]);l=w;d=int(D[spy,j]/2);n=w+d # mirrors: matches unique
  interval=wilson(w,w+l) if w+l else (0,1)
  rows.append([html.escape(names[j]),str(counts[j]),f'{w}–{l}–{d}' if j!=spy else f'{w} matches decisivos espejo',pct(w/(w+l)) if w+l else 'sin dato',pct(win[spy,j]),f'{pct(interval[0])}–{pct(interval[1])}' if w+l else 'sin dato',pct(draw[spy,j])])
 pieces.append(table(['Rival','Plazas 30d','W–L–D de Spy','WR decisivo observado','WR decisivo modelado','IC descriptivo del observado','Empate modelado'],rows))
 paragraph('El WR decisivo modelado es (victorias + 5) / (victorias + derrotas + 10): prior simétrico equivalente a 10 matches para evitar 0%/100% con muestras mínimas. Los empates se estiman aparte con prior Beta(0,5; 9,5), media 5%. Por eso la probabilidad de ganar un match es (1 − empate) × WR decisivo. Los intervalos de la tabla son Wilson descriptivos de matches decisivos, sin corregir agrupación por evento/piloto; no son intervalos ajustados para todo el metajuego. Las celdas sin observaciones son supuestos regularizados, no evidencia de un 50%.')
 focus=[i for i in order if names[i] not in ['Other','Unknown']][:14]
 if spy not in focus:focus[-1]=spy
 mat=np.array([[win[i,j]*100 for j in focus] for i in focus]);samples=nmatch[np.ix_(focus,focus)]
 fig=go.Figure(go.Heatmap(z=mat,x=[names[i] for i in focus],y=[names[i] for i in focus],customdata=samples,colorscale='RdBu',zmid=50,zmin=20,zmax=80,colorbar=dict(title='WR %'),hovertemplate='%{y} vs %{x}<br>WR decisivo modelado: %{z:.1f}%<br>Observaciones: %{customdata}<extra></extra>'))
 chart(fig,'Matriz modelada del field · pasar el cursor para ver la muestra')
 heading('Cómo cambian tus rivales durante el suizo')
 byround=exposure.sum(axis=(0,2));topidx=order[:14]
 fig=go.Figure(go.Heatmap(z=(byround[:,topidx]/N*100).T,x=[f'Ronda {r+1}' for r in range(7)],y=[names[i] for i in topidx],colorscale='Blues',colorbar=dict(title='%'),hovertemplate='%{y} · %{x}: %{z:.2f}%<extra></extra>'))
 chart(fig,'P(enfrentar un rival en cada ronda) · tu plaza de Spy')
 paragraph('Las rondas posteriores se emparejan por puntos, con orden aleatorio dentro del grupo y flotantes al buscar un rival elegible. Se evita repetir oponente y se repara el emparejamiento si hace falta. Es una aproximación al suizo, no una réplica del software del organizador.')
 encounter=[]
 for j in order:
  yes=int(seen[:,j,1:].sum());yeshit=int(seen[1,j,1:].sum());nomiss=int(seen[0,j,0]);nohit=int(seen[1,j,0])
  encounter.append([html.escape(names[j]),pct(yes/N),pct(yeshit/hits),pct(yeshit/yes) if yes else '—',pct(nohit/(nohit+nomiss)) if nohit+nomiss else '—',pct(seen[:,j,2:].sum()/N),fmt(yes)])
 pieces.append(table(['Rival','P(enfrentarlo ≥1)','P(enfrentarlo | top8)','P(top8 | enfrentarlo)','P(top8 | no enfrentarlo)','P(enfrentarlo ≥2)','Tor. expuestos'],encounter))
 paragraph('Las diferencias de las dos últimas probabilidades de clasificación son asociaciones: ganar cambia los futuros oponentes. No interpretarlas como el efecto causal de cruzarse con un mazo.')
 rr=[]
 for rnd,pts,label in [(1,3,'1-0'),(2,6,'2-0'),(2,3,'1-1'),(3,9,'3-0'),(3,6,'2-1'),(4,12,'4-0'),(4,9,'3-1'),(5,12,'4-1'),(6,15,'5-1'),(6,12,'4-2')]:
  a=exposure[:,rnd,pts,:].sum(axis=0);den=int(a.sum());best=np.argsort(-a)[:4]
  rr.append([f'Antes de R{rnd+1}',label+' (puntos equivalentes)',fmt(den),'; '.join(html.escape(names[j])+': '+pct(a[j]/den) for j in best) if den else '—'])
 pieces.append(table(['Momento','Estado','Casos','Rivales más probables'],rr))
 paragraph('El condicionamiento interno usa puntos previos, no W–L–D completo: los estados de la tabla incluyen otros récords que sumen los mismos puntos. Los caminos W/L/D completos se muestran debajo.')
 heading('Los que entran y los que quedan afuera')
 fig=go.Figure()
 for outcome,label,color in [(1,'Top 8','#176d81'),(0,'Fuera','#bf694d')]:
  rec=z['records'][outcome];den=rec.sum();bywins=rec.sum(axis=1)
  fig.add_bar(name=label,x=[str(i) for i in range(8)],y=bywins/den*100,marker_color=color)
 fig.update_xaxes(title='Victorias finales');fig.update_yaxes(title='% dentro de cada grupo')
 chart(fig,'Distribución de victorias finales · clasificados vs no clasificados')
 paragraph(f"En el escenario principal, Spy clasifica {fmt(hits)} veces y queda afuera {fmt(N-hits)}. Entre los eliminados, {pct(tot[3]/(N-hits))} termina con menos puntos que el octavo y {pct(tot[4]/(N-hits))} empata sus puntos y pierde por desempates. El criterio de corte usa puntos, OMW%, GW%, OGW% y sorteo residual. Los marcadores BO3 se suponen 50% 2-0 / 50% 2-1 en matches decisivos y 1-1 en empates: no hay datos suficientes para dar por exactos los desempates de otro torneo.")
 lossrank=np.argsort(-losses[0])[:12]
 fig=go.Figure()
 for out,label,col in [(0,'Fuera','#bf694d'),(1,'Top 8','#176d81')]:
  den=N-hits if out==0 else hits
  fig.add_bar(x=[names[j] for j in lossrank],y=losses[out,lossrank]/den,name=label,marker_color=col)
 fig.update_yaxes(title='Derrotas medias por torneo del grupo')
 chart(fig,'Dónde se acumulan las derrotas · frecuencia y dificultad combinadas')
 paragraph('Este gráfico cuenta derrotas por torneo dentro de cada grupo. Un mazo puede acumular muchas por ser frecuente aunque su matchup no sea especialmente malo. No identifica qué carta, mulligan o decisión produjo la derrota.')
 path=z['paths'];codes=np.argsort(-path[1])[:15];pr=[]
 for c in codes:
  k=c;seq=''
  for _ in range(7):seq='LDW'[k%3]+seq;k//=3
  a=int(path[1,c]);b=int(path[0,c]);pr.append([seq,fmt(a),fmt(b),pct(a/(a+b)) if a+b else '—',pct(a/hits)])
 pieces.append(table(['Camino (W/L/D)','Entraron','Quedaron fuera','P(top8 | camino)','% de todos los top8'],pr))
 heading('Qué conviene preparar')
 paragraph('Los tres cruces de intervención se eligen antes de la corrida por presencia × probabilidad modelada de derrota, entre cruces bajo 50% con al menos cinco observaciones. Se mejora el WR decisivo de todos los pilotos de Spy +2 o +5 puntos porcentuales, conservando la tasa de empates. Los demás cruces y presencias se mantienen. No se atribuye esa mejora a ninguna carta ni se supone que sea gratis en un sideboard real.')
 scen=manifest['scenarios'];sr=[];fig=go.Figure()
 for delta,col in [(.02,'#d3a04a'),(.05,'#176d81')]:
  xs=[];ys=[];errs=[]
  for s in scen:
   if s.get('delta')!=delta:continue
   q=np.load(RES/(s['id']+'.npz'));nn=int(q['totals'][5]);ph=q['totals'][0]/nn
   # Paired batch contrasts use identical seeds for the overlapping central batches.
   base=z['batch_rates'][:len(q['batch_rates'])];diff=q['batch_rates']-base
   change=diff.mean()*100;se=diff.std(ddof=1)/math.sqrt(len(diff))*100
   xs.append(s['target']);ys.append(change);errs.append(1.96*se)
   sr.append([html.escape(s['target']),f'+{int(delta*100)} pp',pct(ph),f'{change:+.3f} pp',f'±{1.96*se:.3f} pp',fmt(nn)])
  fig.add_bar(name=f'+{int(delta*100)} pp de WR',x=xs,y=ys,error_y=dict(type='data',array=errs),marker_color=col)
 fig.update_yaxes(title='Cambio de P(top8), puntos porcentuales')
 chart(fig,'Valor de mejorar un cruce · diferencias con lotes centrales emparejados')
 pieces.append(table(['Rival','Mejora hipotética','P(top8) del escenario','Δ vs lotes centrales pareados','IC 95% MC del Δ','Tor.'],sr))
 paragraph('La referencia pareada de cada intervención son los primeros 250.000 torneos centrales, no el total de 1,5 millones; así se aprovechan semillas compartidas. Los emparejamientos se recalculan cuando cambia un resultado. Las barras de error son del experimento Monte Carlo, no de las mejoras reales de un sideboard.')
 paragraph('Agenda práctica: testear primero los cruces de la tabla, registrando partidas pre/postside y play/draw; separar fallas de ejecución, presión de reloj e interacción del rival. Contrastar las mejoras con la pérdida de consistencia del combo y con los cruces que se sacrifican. Sin tu lista de 75 no corresponde asignar slots concretos ni presentar un sideboard óptimo. La muestra pequeña de varios cruces justifica pruebas adicionales aunque el modelo los estime cerca de 50%.')
 heading('Cuánto depende de la ventana y de los supuestos')
 rr=[]
 for sid,label in [('central30','30 días · central'),('window45','45 días · mismos supuestos'),('parameters30','30 días · parámetros sorteados')]:
  q=np.load(RES/(sid+'.npz'));nn=int(q['totals'][5]);ph=float(q['totals'][0]/nn)
  rr.append([label,fmt(nn),pct(ph)])
 pieces.append(table(['Escenario','Tor.','P(top8) de tu plaza'],rr))
 par=np.load(RES/'parameters30.npz')['batch_rates'];qlo,qhi=np.quantile(par,[.025,.975])
 paragraph(f"En el escenario de parámetros se usan 100 sorteos de metajuego y matriz, con 5.000 torneos por sorteo. El rango percentil 2,5–97,5 de las tasas por lote es {pct(qlo)}–{pct(qhi)}. Incluye ruido de lotes y variación bajo priors independientes Beta/Dirichlet; no es un intervalo calibrado contra eventos nuevos. No modela correlación de pilotos/eventos, cambios regionales, ni incertidumbre por clasificación de listas. Falta validación externa para hablar de precisión predictiva.")
 fig=go.Figure(go.Histogram(x=par*100,nbinsx=15,marker_color='#176d81'));fig.update_xaxes(title='P(top8) estimada por sorteo de parámetros (%)');fig.update_yaxes(title='Sorteos')
 chart(fig,'Incertidumbre del modelo · 100 sorteos de parámetros, 5.000 torneos cada uno')
 heading('Cuántos Spy aparecen en el top 8')
 nn=int(nat['totals'][5]);conv=nat['totals'][2]/nat['totals'][1]
 paragraph(f"Con 110 plazas sorteadas sin forzar Spy: {fmt(nat['totals'][1])} participaciones de Spy y {fmt(nat['totals'][2])} clasificaciones en {fmt(nn)} torneos. Conversión agregada por piloto: {pct(conv)}. Spy clasificados esperados por torneo: {nat['totals'][2]/nn:.3f}. Esto difiere de reservar tu plaza: fijarla aumenta en promedio la cantidad de Spy del field.")
 chart(go.Figure(go.Bar(x=list(range(9)),y=nat['spy_top']/nn*100,marker_color='#176d81')),'Número de Spy en top 8 · field natural')
 heading('Fuentes y reproducibilidad')
 paragraph('Cada evento aceptado tiene una fecha y sede verificadas en la fuente primaria. El índice es MetaMage, filtrado paper, y se utiliza para descubrimiento y alias; la presencia y los matches provienen de las tablas de Melee. No se usó ninguna liga ni evento online. Paupergeddon de julio quedó fuera de ventana y sus archivos no alimentan ningún cálculo.')
 ev=records('events_accepted.csv')
 pieces.append(table(['Evento','Fecha UTC primaria','Sede','Plazas','Matches','Fuente'],[[html.escape(e['name']),e['date'],html.escape(e['venue']),e['players'],e['matches'],f'<a href="{html.escape(e["url"])}" target="_blank" rel="noreferrer">Melee ↗</a>'] for e in sorted(ev,key=lambda e:e['date'],reverse=True)]))
 paragraph('Los eventos excluidos, alias y datos normalizados están en data/processed/. Los originales y respuestas públicas están en data/raw/. El manifiesto fija semillas, tamaños y hashes de entradas; los lotes permiten reanudar sin duplicar torneos. El escenario natural registra como plaza de control el asiento 0 sin forzarlo; sus caminos no se interpretan como caminos de Spy. Los warmups, tests y piloto se excluyen del total de 5M.')
 pieces.append(table(['Escenario','Tor.'],[[s['id'],fmt(s['n'])] for s in scen]))
 paragraph(f"Corrida completada: <b>{fmt(completion['tournaments'])} torneos</b>. Tiempo del proceso de corrida: {completion['wall_seconds']/60:.1f} minutos. Comandos: <code>.venv/bin/python -m unittest discover -s tests -v</code>, <code>.venv/bin/python src/run.py --workers 4</code>, <code>.venv/bin/python src/report.py</code>.")
 paragraph('Limitaciones pendientes: muestra de conveniencia de Melee, mezcla de países y torneos semanales; sin calibración regional; normalización por etiquetas sin clasificar todas las 75; resultados 1-0 por tiempo excluidos; draws parcialmente confundibles con ID; dependencia entre observaciones; ID y drops fuera del motor; política de emparejamiento aproximada; marcadores de juegos supuestos; ninguna recomendación de carta inferida como causal.')
 css='''body{margin:0;background:#f2f0e9;color:#24333f;font:16px/1.65 Arial,sans-serif}main{max-width:1160px;margin:0 auto;padding:55px 28px}h1{font-size:clamp(42px,7vw,80px);line-height:1.05;letter-spacing:-3px;margin:20px 0}h2{font-size:30px;line-height:1.2;margin:60px 0 20px}.eyebrow{letter-spacing:3px;font-size:12px;color:#176d81;font-weight:bold}.lead{font-size:22px;color:#5c6a71}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:15px;margin:30px 0}.card{padding:22px;border-top:4px solid #176d81;background:#fffdf8;border-radius:4px}.card span,.card small{display:block}.card strong{display:block;font-size:36px;color:#176d81}.card small{color:#657078;font-size:12px}.notice{border-left:4px solid #d3a04a;background:#fff8e9;padding:20px}.tablewrap{overflow-x:auto;margin:24px 0;background:#fffdf8}table{border-collapse:collapse;font-size:13px;width:100%}th{text-align:left;background:#e2e9e8;padding:12px;white-space:nowrap}td{padding:10px 12px;border-bottom:1px solid #e7e6df}tbody tr:hover{background:#f0f5f3}a{color:#176d81}code{font-size:12px;background:#e4e6e1;padding:3px}.plotly-graph-div{margin:25px 0;border-radius:5px}@media print{main{max-width:none;padding:0}.plotly-graph-div{break-inside:avoid}.tablewrap{overflow:visible}body{background:white}}'''
 output='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Spy · Caminos al top 8</title><style>'+css+'</style><script>'+get_plotlyjs()+'</script></head><body><main>'+''.join(pieces)+'</main></body></html>'
 (ROOT/'reports/spy_montecarlo.html').write_text(output)
 summary={'central_n':N,'central_hits':hits,'central_rate':rate,'central_mc95':list(wilson(hits,N)),'natural_at_least_one':float(1-nat['spy_top'][0]/nn),'natural_conversion':float(conv),'charts':charts,'sources':len(ev),'parameter_batch_percentiles':[float(qlo),float(qhi)]}
 (RES/'summary.json').write_text(json.dumps(summary,indent=2))
 print('report generated',len(charts),'charts',flush=True)
if __name__=='__main__':main()
