'use strict';
const $=id=>document.getElementById(id),sum=a=>a.reduce((x,y)=>x+y,0),pct=x=>Number.isFinite(x)?(100*x).toLocaleString('es-AR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%':'—',num=x=>Number(x).toLocaleString('es-AR'),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const names=DATA.names,K=names.length,states=DATA.manifest.states,active=names.map((_,i)=>i).filter(i=>DATA.counts[i]>0),cfg={responsive:true,displaylogo:false};
const groups={all:[0,1,2,3,4],miss:[0],top8:[1,2,3,4],top4:[2,3,4],top2:[3,4],champ:[4]},groupLabels={all:'todos los jugadores',miss:'quedaron fuera del top 8',top8:'hicieron top 8',top4:'hicieron top 4',top2:'llegaron a la final',champ:'ganaron el torneo'};
function sortIndices(values){return values.map((_,i)=>i).sort((a,b)=>values[b]-values[a]);}
function table(id,headers,rows){$(id).innerHTML='<div class="tablewrap"><table><thead><tr>'+headers.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(x=>'<td>'+x+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';}
const chartSpecs=new Map();
function plot(id,traces,title,extra={}){chartSpecs.set(id,{traces,layout:{title:{text:title,font:{size:16}},paper_bgcolor:'#fffdf8',plot_bgcolor:'#fffdf8',font:{family:'Arial',color:'#203744'},margin:{l:55,r:25,t:70,b:105},height:450,legend:{orientation:'h',y:1.13},...extra}});}

function card(title,value,note){return '<div class="card">'+esc(title)+'<strong>'+esc(value)+'</strong><small>'+esc(note)+'</small></div>';}
function rec(w,l,d){return d?`${w}–${l}–${d}`:`${w}–${l}`;}
function rate(n,d){return d?n/d:NaN;}
function stateId(r,w,d){return states.findIndex(s=>s[0]===r&&s[1]===w&&s[3]===d);}
let current=null;
let currentView='resumen';
let activeChartFrame=0;
const VIEW_LABELS={resumen:'Resumen',recorridos:'Rivales por ronda',ronda:'Detalle de una ronda',secuencias:'Secuencias W/L/D',ejemplos:'Recorridos completos',eliminatorias:'Eliminatorias',record:'Mesas por récord',presencia:'Presencia de mazos',winrates:'Matriz de win rates',fuentes:'Fuentes y método'};
function syncViewLinks(){
 document.querySelectorAll('[data-view-target]').forEach(link=>{const q=new URLSearchParams(location.search);q.set('view',link.dataset.viewTarget);link.setAttribute('href','?'+q.toString());});
}
function resizeActiveCharts(){
 document.title=VIEW_LABELS[currentView]+' · '+names[+$('deck').value]+' · Pauper';
 if(activeChartFrame)cancelAnimationFrame(activeChartFrame);
 activeChartFrame=requestAnimationFrame(()=>{
  activeChartFrame=0;
  $('panel-'+currentView).querySelectorAll('.chart').forEach(el=>{
   const spec=chartSpecs.get(el.id);if(!spec)return;
   Plotly.react(el,spec.traces,spec.layout,cfg).then(()=>{if(!el.closest('[data-panel]').hidden)return Plotly.Plots.resize(el);});
  });
 });
}

function activateView(view,{push=true,scroll=true}={}){
 currentView=Object.hasOwn(VIEW_LABELS,view)?view:'resumen';
 document.querySelectorAll('[data-panel]').forEach(panel=>{panel.hidden=panel.dataset.panel!==currentView;});
 document.querySelectorAll('.analysis-nav [role=tab]').forEach(link=>{const selected=link.dataset.viewTarget===currentView;link.setAttribute('aria-selected',String(selected));link.tabIndex=selected?0:-1;});
 $('journeyFilters').hidden=!['recorridos','ronda','secuencias','ejemplos'].includes(currentView);
 $('outcomeFilter').hidden=!['recorridos','ronda'].includes(currentView);
 document.querySelector('.analysis-nav').setAttribute('aria-orientation',matchMedia('(max-width:760px)').matches?'horizontal':'vertical');
 updateURL(push);resizeActiveCharts();
 if(scroll)window.scrollTo({top:0,behavior:'auto'});
 if(matchMedia('(max-width:760px)').matches)document.querySelector('.analysis-nav [aria-selected=true]').scrollIntoView({block:'nearest',inline:'nearest'});
}

function journeyData(deck,finishSet,results){return Array.from({length:7},(_,r)=>Array.from({length:K},(_,j)=>sum(results.map(o=>sum(finishSet.map(g=>DATA.journey[deck][r][j][o][g]))))));}
function renderJourneyMatrix(jd,top,rden,group){
 const shown=new Set(top),remaining=active.filter(j=>!shown.has(j));
 const peak=Math.max(0,...top.flatMap(j=>jd.map((row,r)=>rden[r]?row[j]/rden[r]:0)));
 const headers='<thead><tr><th scope="col">Arquetipo rival</th>'+rden.map((n,r)=>`<th scope="col">Ronda ${r+1}<small>${num(n)}<br>encuentros</small></th>`).join('')+'</tr></thead>';
 function cells(counts,label,rest=false){return counts.map((n,r)=>{
  const p=rate(n,rden[r]),intensity=peak&&Number.isFinite(p)?Math.min(1,p/peak):0;
  const background=rest?'#edf0ea':!rden[r]?'#f3f3ee':`rgba(23,107,128,${(.05+.85*intensity).toFixed(3)})`;
  const alpha=.05+.85*intensity;
  const luminance=[255+(23-255)*alpha,253+(107-253)*alpha,248+(128-248)*alpha].map(c=>{const v=c/255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
  const color=!rest&&rden[r]&&1.05/(luminance+.05)>=4.5?'#ffffff':'#000000';
  const detail=`${label}, ronda ${r+1}: ${pct(p)}; ${num(n)} de ${num(rden[r])} encuentros`;
  return `<td data-round="${r+1}" data-count="${n}" data-denominator="${rden[r]}" tabindex="0" title="${esc(detail)}" aria-label="${esc(detail)}" style="background:${background};color:${color}">${pct(p)}</td>`;
 }).join('');}
 let body=top.map(j=>`<tr><th scope="row">${esc(names[j])}</th>${cells(jd.map(row=>row[j]),names[j])}</tr>`).join('');
 if(remaining.length){const counts=jd.map(row=>sum(remaining.map(j=>row[j])));body+=`<tr class="matrix-rest"><th scope="row">Resto de rivales<small>${remaining.length} arquetipos agrupados</small></th>${cells(counts,'Resto de rivales',true)}</tr>`;}
 const total='<tfoot><tr><th scope="row">Total de la ronda</th>'+rden.map(n=>`<td>${n?'100%':'—'}</td>`).join('')+'</tr></tfoot>';
 $('journeyHeat').innerHTML=`<div class="matrix-heading"><h3>Rivales por ronda · ${esc(groupLabels[group])}</h3><p>Leé una columna para ver a quiénes enfrentaron en esa ronda. Leé una fila para seguir cómo cambia un rival durante el torneo.</p></div><div class="matrix-legend"><span>Menor frecuencia</span><span class="matrix-gradient" aria-hidden="true"></span><span>Mayor frecuencia</span><span class="matrix-percent">Cada celda muestra el % de encuentros de su columna.</span></div><p class="matrix-mobile-hint">Deslizá la matriz hacia los costados para ver las siete rondas.</p><div class="matrix-scroll" tabindex="0" role="region" aria-label="Matriz de arquetipos rivales por ronda"><table aria-label="Porcentaje de rivales en cada ronda"><caption>Los ${top.length} rivales más frecuentes del recorrido; los demás se agrupan al final. Cada columna suma 100%, salvo redondeo. El denominador respeta los filtros de jugadores y de resultado.</caption>${headers}<tbody>${body}</tbody>${total}</table></div>`;
}
function renderGlobalRankings(){
 const specs=[['champions',6,'Más campeones'],['top2',5,'Más Top 2'],['top4',4,'Más Top 4'],['top8',1,'Más Top 8']];
 $('globalRankings').innerHTML=specs.map(([id,,label])=>`<details open data-ranking="${id}"><summary>Top 20 · ${label}</summary><div id="ranking-${id}"></div></details>`).join('');
 for(const [id,col] of specs){
  const total=sum(DATA.totals.map(t=>t[col])),order=[...active].sort((a,b)=>DATA.totals[b][col]-DATA.totals[a][col]||names[a].localeCompare(names[b])).slice(0,20);
  table('ranking-'+id,['Puesto','Arquetipo','Cantidad','% de los resultados','% por participación'],order.map((d,i)=>[i+1,esc(names[d]),num(DATA.totals[d][col]),pct(rate(DATA.totals[d][col],total)),pct(rate(DATA.totals[d][col],DATA.totals[d][0]))]));
 }
}
function renderJourney(){
 const deck=+$('deck').value,group=$('group').value,gs=groups[group],outcome=$('outcome').value,os=outcome==='all'?[0,1,2]:[+outcome],t=DATA.totals[deck];
 const gp=group==='all'?t[0]:group==='miss'?t[0]-t[1]:t[{top8:1,top4:4,top2:5,champ:6}[group]];
 current={...(current||{}),deck,group,gs,os,gp};
 $('headline').textContent=`${names[deck]} · ${group==='all'?'recorridos de todos los jugadores':'recorridos de los que '+groupLabels[group]}`;
 $('odds').innerHTML=card('Top 8',pct(t[1]/t[0]),num(t[1])+' clasificaciones')+card('Top 4',pct(t[4]/t[0]),num(t[4])+' semifinalistas')+card('Top 2',pct(t[5]/t[0]),num(t[5])+' finalistas')+card('Campeón',pct(t[6]/t[0]),num(t[6])+' títulos');
 $('groupInfo').innerHTML=`<b>${num(gp)} participaciones de ${esc(names[deck])}</b> en el grupo elegido, sobre ${num(t[0])} participaciones de este arquetipo en los mismos ${num(DATA.completion.tournaments)} torneos. Cada participación aporta un recorrido de siete rondas. `+(DATA.counts[deck]<10?'<b>Hay menos de diez plazas reales de este arquetipo en la muestra presencial: el modelo tiene una base limitada.</b> ':'');
 const jd=journeyData(deck,gs,os),all=journeyData(deck,[0,1,2,3,4],os),rest=all.map((row,r)=>row.map((x,j)=>x-jd[r][j]));
 current.jd=jd;
 const frequencies=names.map((_,j)=>sum(jd.map(a=>a[j]))),top=sortIndices(frequencies).filter(j=>frequencies[j]>0).slice(0,16),rden=jd.map(sum);
 renderJourneyMatrix(jd,top,rden,group);
 const outcomeCounts=[0,1,2].map(o=>Array.from({length:7},(_,r)=>sum(names.map((_,j)=>sum(gs.map(g=>DATA.journey[deck][r][j][o][g]))))));
 plot('journeyResults',[2,0,1].map(o=>({type:'bar',name:['Derrotas','Empates','Victorias'][o],x:[1,2,3,4,5,6,7],y:outcomeCounts[o].map(n=>gp?100*n/gp:0),customdata:outcomeCounts[o],marker:{color:['#bd705a','#d4ad61','#176b80'][o]},hovertemplate:'R%{x}: %{y:.2f}% · %{customdata}<extra>%{fullData.name}</extra>'})), 'Victorias, derrotas y empates por ronda',{barmode:'stack',yaxis:{range:[0,100],title:{text:'% de participaciones del grupo'}},xaxis:{title:{text:'Ronda suiza'}}});
 $('journeyResultsInfo').innerHTML=`<b>Cómo leer los resultados por ronda:</b> cada barra distribuye las ${num(gp)} participaciones de ${esc(names[deck])} del grupo «${esc(groupLabels[group])}» entre victorias, derrotas y empates en esa ronda. Por ejemplo, 70% de victorias en R2 significa que el 70% de ese grupo ganó su segunda ronda. Cada barra con datos suma 100%. El grupo se define por cómo terminó el torneo; al elegir «hicieron top 8», seguimos retrospectivamente a quienes clasificaron. Este gráfico siempre incluye los tres resultados, aunque filtres encuentros ganados o perdidos. El detalle de qué arquetipos enfrentaron está en la matriz y en «Detalle de una ronda».`;
 const restFreq=names.map((_,j)=>sum(rest.map(row=>row[j]))),dn=sum(frequencies),dr=sum(restFreq),compare=top.slice(0,10);
 plot('journeyComparison',[{type:'bar',name:'Grupo elegido',x:compare.map(j=>names[j]),y:compare.map(j=>dn?100*frequencies[j]/dn:0),marker:{color:'#176b80'}},{type:'bar',name:'Resto de jugadores del mazo',x:compare.map(j=>names[j]),y:compare.map(j=>dr?100*restFreq[j]/dr:0),marker:{color:'#d4ad61'}}],'Rivales del grupo y del resto · % de encuentros');
 renderHistory();
 const codes=sortIndices(DATA.paths[deck].map(v=>sum(gs.map(g=>v[g])))).slice(0,12),pathRows=[];
 for(const code of codes){let k=code,seq='';for(let r=0;r<7;r++){seq='LDW'[k%3]+seq;k=Math.floor(k/3);}const n=sum(gs.map(g=>DATA.paths[deck][code][g]));if(n)pathRows.push([seq,num(n),pct(rate(n,gp))]);}
 table('journeyPaths',['Secuencia del suizo','Participaciones en el grupo','% del grupo'],pathRows);
 const examples=[];
 for(const g of gs)for(let k=0;k<4;k++){const id=DATA.examples.ids[deck][g][k];if(id[0]>=0)examples.push({g,k,id});}
 examples.sort((a,b)=>a.id[0]-b.id[0]||a.id[1]-b.id[1]);
 const labels=['Fuera del top 8','Top 8','Top 4','Subcampeón','Campeón'];
 table('examplePaths',['Torneo / jugador','Finalizó',...Array.from({length:7},(_,r)=>'R'+(r+1)),'Cuartos','Semifinal','Final'],examples.slice(0,10).map(e=>['#'+(e.id[0]+1)+' / '+(e.id[1]+1),labels[e.g],...DATA.examples.opponents[deck][e.g][e.k].map((j,r)=>j<0?'—':esc(names[j])+' · <b>'+['L','D','W'][DATA.examples.results[deck][e.g][e.k][r]]+'</b>')]));
 renderPlayoffs();renderState();renderSources();updateURL();resizeActiveCharts();
}
function renderHistory(){
 const {deck,gs,os,jd}=current,r=+$('historyRound').value,den=sum(jd[r]),ordered=sortIndices(jd[r]);
 table('historyTable',['Rival','% de encuentros filtrados','Encuentros filtrados','Victorias del grupo','Derrotas del grupo','Empates del grupo'],ordered.filter(j=>jd[r][j]>0).map(j=>[esc(names[j]),pct(rate(jd[r][j],den)),num(jd[r][j]),...[2,0,1].map(o=>num(sum(gs.map(g=>DATA.journey[deck][r][j][o][g]))))]));
 const top=ordered.filter(j=>jd[r][j]>0).slice(0,3);
 $('roundNarrative').innerHTML=`En la ronda ${r+1}, el grupo seleccionado tuvo <b>${num(den)} encuentros</b> que cumplen el filtro de resultado. `+(den?'Los rivales más frecuentes fueron '+top.map(j=>esc(names[j])+' ('+pct(jd[r][j]/den)+')').join(', ')+'.':'No hay observaciones para este filtro.');
}
function renderPlayoffs(){
 const d=current.deck,t=DATA.totals[d],counts=[t[1],t[4],t[5]],stageNames=['Cuartos · top 8','Semifinal · top 4','Final · top 2'];
 const per=Array.from({length:3},(_,r)=>names.map((_,j)=>sum(DATA.playoffs[d][r][j]))),order=sortIndices(names.map((_,j)=>sum(per.map(row=>row[j])))).filter(j=>sum(per.map(row=>row[j]))>0).slice(0,12);
 plot('playoffRivals',[{type:'heatmap',x:stageNames,y:order.map(j=>names[j]),z:order.map(j=>per.map((row,r)=>counts[r]?100*row[j]/counts[r]:null)),colorscale:[[0,'#eef4f2'],[0.5,'#83b5bc'],[1,'#176b80']],hovertemplate:'%{x} · %{y}: %{z:.2f}%<extra></extra>'}],'Rivales en cada eliminatoria',{margin:{l:145,r:25,t:70,b:65},yaxis:{autorange:'reversed'}});
 plot('playoffConversion',[{type:'bar',x:['Top 8 → top 4','Top 4 → final','Final → título'],y:[rate(t[4],t[1])*100,rate(t[5],t[4])*100,rate(t[6],t[5])*100],marker:{color:'#176b80'},hovertemplate:'%{x}: %{y:.2f}%<extra></extra>'}],'Probabilidad de ganar cada eliminatoria',{yaxis:{range:[0,100],title:{text:'% condicionado a haber llegado'}}});
 const rows=[];for(let r=0;r<3;r++)for(const j of sortIndices(per[r]).filter(j=>per[r][j]>0)){const [l,w]=DATA.playoffs[d][r][j];rows.push([stageNames[r],esc(names[j]),num(w),num(l),pct(rate(w+l,counts[r])),pct(rate(w,w+l))]);}
 table('playoffTable',['Instancia','Rival','Victorias','Derrotas','% de rivales de esta instancia','% ganado en simulación'],rows);
}
function fillRecords(preferred){
 const r=+$('round').value-1;const ss=states.map((s,i)=>({s,i})).filter(x=>x.s[0]===r).sort((a,b)=>b.s[1]-a.s[1]||a.s[3]-b.s[3]);
 $('record').innerHTML=ss.map(x=>`<option value="${x.i}">${rec(x.s[1],x.s[2],x.s[3])}</option>`).join('');
 $('record').value=ss.some(x=>x.i===preferred)?String(preferred):String(ss[0].i);
}
function stateRows(d,s){const x=DATA.exposure[d][s].map(v=>sum(v)),den=sum(x),se=DATA.mc_se[d][s];return sortIndices(x).filter(j=>DATA.counts[j]>0).map(j=>{const p=rate(x[j],den),o=DATA.outcomes[d][s][j],n=sum(o),base=DATA.counts[j]/sum(DATA.counts);return [names[j],p,den,x[j],se[j],base,rate(o[2],n),rate(DATA.exposure[d][s][j][1],x[j])];});}
function renderState(){
 if(!current)return;const d=current.deck,s=+$('record').value,[r,w,l,dr]=states[s],x=DATA.exposure[d][s].map(sum),den=sum(x),st=DATA.state_tournaments[d][s],placements=DATA.state_placements[d][s];current.state=s;
 $('query').textContent=`${names[d]} · ${rec(w,l,dr)} antes de la ronda ${r+1}`;
 $('stateCards').innerHTML=card('Casos de este récord',num(den),'Participaciones del arquetipo')+card('Tor. que aportaron casos',num(st),'De los 5 millones de torneos')+card('Top 8 desde aquí',pct(rate(sum(placements.slice(1)),den)),'Condicionado a llegar a este récord')+card('Campeón desde aquí',pct(rate(placements[4],den)),'Incluye suizo restante y eliminatorias');
 const top=sortIndices(x).filter(j=>x[j]>0).slice(0,13),base=sum(DATA.counts),se=DATA.mc_se[d][s];
 plot('rivals',[{type:'bar',x:top.map(j=>names[j]),y:top.map(j=>100*x[j]/den),error_y:{type:'data',array:top.map(j=>196*se[j])},marker:{color:'#176b80'},customdata:top.map(j=>x[j]),hovertemplate:'%{x}: %{y:.2f}% · %{customdata}<extra></extra>'}],'Próximo rival · récord exacto',{yaxis:{title:{text:'Probabilidad (%)'}}});
 plot('enrichment',[{type:'bar',name:'En esta mesa',x:top.map(j=>names[j]),y:top.map(j=>100*x[j]/den),marker:{color:'#176b80'}},{type:'bar',name:'Presencia inicial',x:top.map(j=>names[j]),y:top.map(j=>100*DATA.counts[j]/base),marker:{color:'#d4ad61'}}],'Mesa actual frente al metajuego inicial');
 const rows=stateRows(d,s).map(v=>{const [name,p,n,k,se,base,wr,qual]=v;return [esc(name),pct(p),k&&n?pct(Math.max(0,p-1.96*se))+'–'+pct(Math.min(1,p+1.96*se)):'sin estimación',num(k),pct(base),pct(wr),pct(qual)];});
 table('ranking',['Rival','P(enfrentarlo aquí)','IC95% Monte Carlo','Encuentros','Presencia inicial','% de matches ganados aquí','P(top8 | este encuentro)'],rows);
 const ss=states.map((s,i)=>({s,i})).filter(a=>a.s[0]===r&&a.s[3]===0).sort((a,b)=>b.s[1]-a.s[1]);const common=sortIndices(DATA.counts).filter(j=>DATA.counts[j]>0).slice(0,15);
 plot('heat',[{type:'heatmap',x:ss.map(a=>rec(a.s[1],a.s[2],0)),y:common.map(j=>names[j]),z:common.map(j=>ss.map(a=>{const row=DATA.exposure[d][a.i].map(sum),n=sum(row);return n?100*row[j]/n:null;})),colorscale:[[0,'#eef4f2'],[0.5,'#83b5bc'],[1,'#176b80']],hovertemplate:'%{y} · récord %{x}: %{z:.2f}%<extra></extra>'}],`Ronda ${r+1} · cómo cambia el rival con el récord`,{margin:{l:145,r:25,t:70,b:60},height:480,yaxis:{autorange:'reversed'}});
 const opp=DATA.opp_records[d][s],rp=sortIndices(opp).filter(k=>opp[k]>0);
 table('oppRecords',['Récord previo del oponente','Encuentros','Probabilidad'],rp.map(k=>{const ow=Math.floor(k/7),od=k%7,ol=r-ow-od;return [rec(ow,ol,od),num(opp[k]),pct(rate(opp[k],den))];}));
 updateURL();resizeActiveCharts();
}
function renderSources(){
 const d=current.deck,s=DATA.sources,den=sum(DATA.counts),order=sortIndices(DATA.counts).filter(j=>DATA.counts[j]>0),w=DATA.W,dd=DATA.D;
 table('meta',['Arquetipo','Plazas presenciales','Presencia','Esperados en 110'],order.map(j=>[esc(names[j]),num(DATA.counts[j]),pct(DATA.counts[j]/den),(110*DATA.counts[j]/den).toFixed(2)]));
 $('matrixInfo').innerHTML=`<p>Presencia: <b>${s.paper_entries} de ${s.paper_entries_total} plazas de ${s.paper_events} eventos presenciales</b> (${(s.coverage*100).toFixed(1)}% de cobertura). Se recuperaron ${s.recovered_entries} participaciones mediante las cartas de sus listas. Se excluyeron ${s.excluded_entries} plazas sin clasificación suficiente y sus encuentros. La presencia se renormaliza al 100% sobre las plazas identificadas. Matriz: ${num(s.paper_matches)} matches presenciales + ${s.online_matches} matches de eliminatorias publicadas de ${s.online_events} eventos MTGO. Ventana inclusiva: 20/09–19/10/2026. El online tiene peso 1 por match y nunca entra al porcentaje de presencia.</p><p>La muestra online está seleccionada por top 8; aumentar el número de matches no garantiza eliminar sesgos. Cada celda se regulariza con 10 matches decisivos equivalentes al 50%: (W+5)/(W+L+10). Los empates se modelan por separado. Un cruce sin observaciones es un supuesto, no evidencia de 50%.</p>`;
 const focus=order.slice(0,16);if(!focus.includes(d))focus[focus.length-1]=d;
 plot('wrMatrix',[{type:'heatmap',x:focus.map(j=>names[j]),y:focus.map(j=>names[j]),z:focus.map(i=>focus.map(j=>100*DATA.win[i][j])),customdata:focus.map(i=>focus.map(j=>sum([0,1].map(q=>w[q][i][j]+w[q][j][i]+dd[q][i][j])))),zmid:50,zmin:20,zmax:80,colorscale:'RdBu',hovertemplate:'%{y} vs %{x}: %{z:.1f}%<br>Registros: %{customdata}<extra></extra>'}],'WR decisivo modelado · filas contra columnas',{height:550,margin:{l:150,r:25,t:70,b:140}});
 table('matchups',['Rival','Papel W–L–D','Online W–L–D','WR decisivo modelado','P(empate)','P(ganar match)'],order.map(j=>[esc(names[j]),...[0,1].map(q=>j===d?'Espejo: '+num(w[q][d][d])+' matches decisivos':`${w[q][d][j]}–${w[q][j][d]}–${dd[q][d][j]}`),pct(DATA.win[d][j]),pct(DATA.draw[d][j]),pct((1-DATA.draw[d][j])*DATA.win[d][j])]));
 $('method').innerHTML=`<p><b>Una única corrida final:</b> ${num(DATA.completion.tournaments)} torneos, ${num(DATA.completion.player_paths)} participaciones, ${num(DATA.completion.swiss_matches)} matches suizos y ${num(DATA.completion.playoff_matches)} matches de eliminatorias. No se reserva una plaza para ningún arquetipo: se sortean las 110 por multinomial usando presencia presencial.</p><p>Todos los jugadores se registran antes de cada ronda por W/L/D exacto, rival, resultado y resultado final del torneo. Se distinguen cinco desenlaces: fuera del top8, eliminado en cuartos, eliminado en semifinales, subcampeón y campeón. Top8/top4/top2 agrupan los desenlaces correspondientes. No son corridas independientes por mazo ni por filtro.</p><p>Suizo aproximado: orden por puntos y azar dentro del grupo, flotantes y prevención de revancha. No hay drops, ID, byes ni diferencias de habilidad. Corte por puntos, OMW%, GW%, OGW% y azar residual. Se suponen marcadores 50% 2-0 / 50% 2-1 y empate 1-1 para desempates. Top8 a eliminación directa por seeds y WR decisivo; no se ajusta la elección de play/draw. Los empates suizos usan el modelo de cada cruce.</p><p>Se verificaron sedes físicas, fecha primaria, tablas completas de primera ronda y rondas suizas en Melee. Los IDs/0-0, byes, concesiones marcadas y victorias por tiempo sin dos juegos ganados se excluyen del ajuste. Algunos empates pactados después de jugar no son distinguibles. Para MTGO solo se usan resultados individuales de brackets públicos y etiquetas del índice MetaMage, nunca récords globales para inferir parejas. Se excluyeron cinco páginas sin payload primario de partidas.</p><p>Incertidumbre: los porcentajes son condicionales al field y a la matriz modelados, no predicciones regionales calibradas. El IC de próximos rivales usa 100 lotes independientes de 50.000 torneos y contempla agrupación dentro de un torneo; no incluye error de datos ni sesgos de selección. Las etiquetas pueden reunir variantes. Se excluyen las participaciones sin arquetipo identificable y sus matches; el field simulado se limita a las plazas identificadas, renormalizadas al 100%. Las asociaciones entre rivales y clasificación no establecen causalidad.</p><p>Fuentes normalizadas: <code>data/processed/classified/</code>. Manifiesto, hashes, conteos finales y agregados: <code>results/classified/</code>. Reproducir: <code>python src/classify_decks.py --fetch</code>, <code>python src/classify_online.py</code>, <code>python src/build_model_classified.py</code>, <code>python src/run_classified.py</code>, <code>python src/replay_classified.py</code>, <code>python src/report_tournament.py</code>. Tiempo de corrida: ${(DATA.completion.wall_seconds/60).toFixed(1)} minutos.</p>`;
}
function downloadCSV(all){
 const d=current.deck,ss=all?states.map((_,i)=>i):[current.state],rows=[['arquetipo','proxima_ronda','victorias','derrotas','empates','rival','probabilidad','encuentros','casos_del_record','torneos_con_record','meta_presencial','gano_sim','empato_sim','perdio_sim','luego_top8']];
 for(const s of ss){const [r,w,l,dr]=states[s],den=sum(DATA.exposure[d][s].map(sum));for(const j of active){const n=sum(DATA.exposure[d][s][j]),o=DATA.outcomes[d][s][j];rows.push([names[d],r+1,w,l,dr,names[j],den?n/den:'',n,den,DATA.state_tournaments[d][s],DATA.counts[j]/sum(DATA.counts),o[2],o[1],o[0],DATA.exposure[d][s][j][1]]);}}
 const csv=rows.map(row=>row.map(x=>'"'+String(x).replace(/"/g,'""')+'"').join(',')).join('\n'),url=URL.createObjectURL(new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8;'}));const a=document.createElement('a');a.href=url;a.download='recorridos_'+names[d].replace(/ /g,'_')+(all?'_todos':'_consulta')+'.csv';a.click();URL.revokeObjectURL(url);
}
function updateURL(push=false){if(!current)return;const s=states[+$('record').value];if(!s)return;const q=new URLSearchParams({view:currentView,deck:names[current.deck],group:$('group').value,outcome:$('outcome').value,hr:String(+$('historyRound').value+1),r:String(s[0]+1),w:String(s[1]),d:String(s[3])});const next='?'+q.toString();try{if(push&&next!==location.search)history.pushState(null,'',next);else history.replaceState(null,'',next);}catch{}syncViewLinks();}

$('round').innerHTML=[1,2,3,4,5,6,7].map(r=>`<option value="${r}">Ronda ${r}</option>`).join('');$('historyRound').innerHTML=[0,1,2,3,4,5,6].map(r=>`<option value="${r}">Ronda ${r+1}</option>`).join('');
function restoreControlsFromURL(){
 const q=new URLSearchParams(location.search),di=names.indexOf(q.get('deck')||'Spy Combo');
 $('deck').value=String(active.includes(di)?di:names.indexOf('Spy Combo'));
 $('group').value=Object.hasOwn(groups,q.get('group'))?q.get('group'):'top8';
 $('outcome').value=['all','0','1','2'].includes(q.get('outcome'))?q.get('outcome'):'all';
 const hr=Number(q.get('hr')||1);$('historyRound').value=String(hr>=1&&hr<=7?hr-1:0);
 const qr=Number(q.get('r')||1);$('round').value=String(qr>=1&&qr<=7?qr:1);
 fillRecords(stateId(+$('round').value-1,Number(q.get('w')||0),Number(q.get('d')||0)));
 currentView=Object.hasOwn(VIEW_LABELS,q.get('view'))?q.get('view'):'resumen';
}
restoreControlsFromURL();
renderGlobalRankings();

$('deck').addEventListener('change',renderJourney);$('group').addEventListener('change',renderJourney);$('outcome').addEventListener('change',renderJourney);$('historyRound').addEventListener('change',()=>{renderHistory();updateURL();});$('round').addEventListener('change',()=>{fillRecords(-1);renderState();});$('record').addEventListener('change',renderState);$('download').addEventListener('click',()=>downloadCSV(false));$('downloadAll').addEventListener('click',()=>downloadCSV(true));$('share').addEventListener('click',async()=>{updateURL();try{await navigator.clipboard.writeText(location.href);$('shareStatus').textContent='Link copiado';}catch{$('shareStatus').textContent=location.href;}});document.querySelectorAll('details').forEach(el=>el.addEventListener('toggle',()=>{if(el.open)window.dispatchEvent(new Event('resize'));}));renderJourney();activateView(currentView,{push:false,scroll:false});

document.querySelectorAll('[data-view-target]').forEach(link=>link.addEventListener('click',event=>{
 if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
 event.preventDefault();activateView(link.dataset.viewTarget);
}));
document.querySelector('.analysis-nav').addEventListener('keydown',event=>{
 const tabs=[...document.querySelectorAll('.analysis-nav [role=tab]')],i=tabs.indexOf(document.activeElement);if(i<0)return;
 let next;if(['ArrowDown','ArrowRight'].includes(event.key))next=(i+1)%tabs.length;else if(['ArrowUp','ArrowLeft'].includes(event.key))next=(i+tabs.length-1)%tabs.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=tabs.length-1;else return;
 event.preventDefault();activateView(tabs[next].dataset.viewTarget,{scroll:false});tabs[next].focus();
});
window.addEventListener('popstate',()=>{restoreControlsFromURL();renderJourney();activateView(currentView,{push:false,scroll:false});});
window.addEventListener('resize',()=>{document.querySelector('.analysis-nav').setAttribute('aria-orientation',matchMedia('(max-width:760px)').matches?'horizontal':'vertical');});
