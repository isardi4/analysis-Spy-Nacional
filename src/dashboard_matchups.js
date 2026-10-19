/* Independent pair explorer; the simulation and its input model stay unchanged. */
function intervalLabel(ci){return ci?`${pct(ci[0])} – ${pct(ci[1])}`:'Sin estimación';}
function renderMatchupMatrix(){
 const mode=$('matchupMode').value,matchupOrder=[...active].sort((a,b)=>DATA.counts[b]-DATA.counts[a]||names[a].localeCompare(names[b])).slice(0,20);
 const head='<thead><tr><th scope="col">Fila vs. columna</th>'+matchupOrder.map(j=>`<th scope="col"><span>${esc(names[j])}</span></th>`).join('')+'</tr></thead>';
 const body=matchupOrder.map(a=>'<tr><th scope="row">'+esc(names[a])+'</th>'+matchupOrder.map(b=>{
  const s=matchupStats(DATA.W,DATA.D,a,b),p=s.mirror?.5:mode==='model'?s.adjusted:s.observed;
  const label=s.mirror?'50%':p===null?'—':(100*p).toLocaleString('es-AR',{maximumFractionDigits:1,minimumFractionDigits:1})+'%';
  const detail=`${names[a]} contra ${names[b]}. ${s.mirror?'Espejo: 50% por simetría':`WR observado: ${s.observed===null?'sin muestra':pct(s.observed)}. IC 95% Wilson: ${intervalLabel(s.ci)}. Ajustado: ${pct(s.adjusted)}`}. ${s.n} matches decisivos, ${s.d} empates. Abrir comparador.`;
  const bg=s.mirror||p===.5?'#e8ece8':p===null?'#f0f0ed':p>.5?`rgba(23,107,128,${(.08+.5*Math.abs(p-.5)*2).toFixed(3)})`:`rgba(189,112,90,${(.08+.5*Math.abs(p-.5)*2).toFixed(3)})`;
  return `<td style="background:${bg}"><button type="button" data-matchup-a="${a}" data-matchup-b="${b}" title="${esc(detail)}" aria-label="${esc(detail)}">${label}<small>n=${num(s.n)}</small></button></td>`;
 }).join('')+'</tr>').join('');
 $('matchupMatrix').innerHTML='<div class="matchup-scroll" role="region" aria-label="Matriz 20 por 20 de win rates" tabindex="0"><table><caption>20 arquetipos con mayor presencia presencial. Cada celda es el WR del mazo de la fila contra el de la columna. n cuenta matches decisivos observados, sin empates; cada espejo cuenta una sola vez. El color representa el WR, no su confianza. Seleccioná una celda para ver sus datos.</caption>'+head+'<tbody>'+body+'</tbody></table></div>';
}
function renderMatchupPair(){
 const a=+$('matchupA').value,b=+$('matchupB').value,s=matchupStats(DATA.W,DATA.D,a,b);
 $('matchupHeading').textContent=names[a]+' contra '+names[b];
 $('matchupCards').innerHTML=card('WR observado',s.mirror?'50% nominal':s.observed===null?'Sin muestra':pct(s.observed),'Victorias / (victorias + derrotas), sin empates')+card('IC 95% · Wilson',s.mirror?'No aplica':intervalLabel(s.ci),'Incertidumbre del WR observado')+card('WR usado en simulación',pct(DATA.win[a][b]),'Ajustado con 5 victorias y 5 derrotas previas')+card('Desvío posterior',s.mirror?'No aplica':(100*s.posteriorSD).toLocaleString('es-AR',{maximumFractionDigits:2,minimumFractionDigits:2})+' pp','Desviación estándar de la estimación ajustada');
 $('matchupEvidence').innerHTML=s.mirror?`<b>Espejo:</b> ${num(s.n)} matches decisivos y ${num(s.d)} empates entre jugadores del mismo arquetipo. Cada encuentro se cuenta una vez. El 50% se fija por simetría; no se estima una ventaja del arquetipo sobre sí mismo ni un intervalo binomial con resultados duplicados.`:s.n?`<b>${num(s.total)} matches observados:</b> ${num(s.w)} victorias, ${num(s.l)} derrotas y ${num(s.d)} empates desde la perspectiva de ${esc(names[a])}. El intervalo usa los ${num(s.n)} matches decisivos. ${s.ci[0]<=.5&&s.ci[1]>=.5?'El intervalo incluye 50%: estos datos no distinguen con claridad una ventaja frente a un cruce parejo.':'El intervalo queda '+(s.ci[0]>.5?'por encima':'por debajo')+' de 50% bajo el supuesto binomial.'}`:`<b>Sin matches decisivos observados.</b> ${s.d?`Hay ${num(s.d)} empates.`:'No hay resultados de este cruce en la muestra.'} El 50% ajustado proviene del prior; no demuestra que el matchup sea parejo. El desvío posterior refleja ese supuesto inicial.`;
 const rows=[['Papel',[0]],['Online · playoffs publicados',[1]],['Total',[0,1]]].map(([label,qs])=>{
  const r=matchupStats(DATA.W,DATA.D,a,b,qs);return [label,r.mirror?'—':num(r.w),r.mirror?'—':num(r.l),num(r.d),num(r.n),num(r.total),r.mirror?'50% nominal':r.observed===null?'Sin muestra':pct(r.observed),r.mirror?'No aplica':intervalLabel(r.ci)];
 });
 table('matchupSourceTable',['Fuente','Victorias A','Derrotas A','Empates','Decisivos','Matches','WR observado','IC 95% Wilson'],rows);
 const traces=[];
 if(s.ci)traces.push({type:'scatter',mode:'markers',name:'Observado · IC 95%',x:[100*s.observed],y:['WR decisivo'],error_x:{type:'data',symmetric:false,array:[100*(s.ci[1]-s.observed)],arrayminus:[100*(s.observed-s.ci[0])],visible:true},marker:{size:12,color:'#176b80'},hovertemplate:'WR observado: %{x:.2f}%<extra></extra>'});
 traces.push({type:'scatter',mode:'markers',name:'Usado en simulación',x:[100*DATA.win[a][b]],y:['WR decisivo'],marker:{size:12,symbol:'diamond',color:'#bd705a'},hovertemplate:'WR modelado: %{x:.2f}%<extra></extra>'});
 plot('matchupInterval',traces,'Observado y ajustado',{height:285,margin:{l:95,r:25,t:65,b:65},xaxis:{range:[0,100],title:{text:'Win rate decisivo (%)'}},yaxis:{fixedrange:true},shapes:[{type:'line',x0:50,x1:50,y0:0,y1:1,yref:'paper',line:{dash:'dot',color:'#8a9998'}}]});
 table('matchupMatchProbabilities',['Resultado del próximo match · modelo','Probabilidad'],[['Victoria de '+esc(names[a]),pct((1-DATA.draw[a][b])*DATA.win[a][b])],['Empate',pct(DATA.draw[a][b])],['Derrota de '+esc(names[a]),pct((1-DATA.draw[a][b])*(1-DATA.win[a][b]))]]);
 updateURL();resizeActiveCharts();
}
function initMatchupExplorer(){
 const opts=names.map((n,i)=>`<option value="${i}">${esc(n)}</option>`).join('');$('matchupA').innerHTML=opts;$('matchupB').innerHTML=opts;
 $('matchupA').addEventListener('change',renderMatchupPair);$('matchupB').addEventListener('change',renderMatchupPair);
 $('matchupSwap').addEventListener('click',()=>{const a=$('matchupA').value;$('matchupA').value=$('matchupB').value;$('matchupB').value=a;renderMatchupPair();});
 $('matchupMode').addEventListener('change',()=>{renderMatchupMatrix();updateURL();});
 $('matchupMatrix').addEventListener('click',e=>{const cell=e.target.closest('[data-matchup-a]');if(!cell)return;$('matchupA').value=cell.dataset.matchupA;$('matchupB').value=cell.dataset.matchupB;renderMatchupPair();$('matchupHeading').scrollIntoView({block:'start',behavior:'auto'});});
}
