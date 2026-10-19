const {chromium}=require('/private/tmp/spy-browser/node_modules/playwright-core');const path=require('path');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];let remote=0;
 page.on('pageerror',e=>errors.push(String(e)));await page.route('http://**/*',r=>{remote++;return r.abort()});await page.route('https://**/*',r=>{remote++;return r.abort()});
 await page.goto('file://'+path.resolve('reports/metagame_explorer.html'));await page.waitForFunction(()=>!!document.querySelector('#odds strong'));
 if(process.argv.includes('--matrix-only')){
  let checked=0;
  for(const g of ['all','miss','top8','top4','top2','champ'])for(const o of ['all','0','1','2']){
   await page.selectOption('#group',g);await page.selectOption('#outcome',o);
   const result=await page.evaluate(()=>{
    const rows=[...document.querySelectorAll('#journeyHeat tbody tr')];
    return {columns:document.querySelectorAll('#journeyHeat thead th').length,rows:rows.length,
     complete:rows.every(row=>row.querySelectorAll('td').length===7),
     conserved:Array.from({length:7},(_,r)=>rows.reduce((n,row)=>n+Number(row.querySelectorAll('td')[r].dataset.count),0)===sum(current.jd[r])).every(Boolean),
     readable:rows.every(row=>[...row.querySelectorAll('td')].every(cell=>cell.textContent.includes('%')||cell.textContent==='—'))};
   });
   if(result.columns!==8||!result.complete||!result.conserved||!result.readable)throw Error('Invalid matrix '+g+' '+o+' '+JSON.stringify(result));checked++;
  }
  await page.selectOption('#group','top8');await page.selectOption('#outcome','all');
  await page.locator('#journeyHeat').screenshot({path:'reports/journey_matrix_desktop.png'});
  await page.setViewportSize({width:390,height:844});await page.waitForTimeout(400);
  const mobile=await page.evaluate(()=>{const sc=document.querySelector('.matrix-scroll');const first=sc.querySelector('tbody th');const before=first.getBoundingClientRect().left;sc.scrollLeft=280;return {pageOverflow:document.documentElement.scrollWidth>innerWidth+2,scrollable:sc.scrollWidth>sc.clientWidth,scrolled:sc.scrollLeft>0,sticky:Math.abs(first.getBoundingClientRect().left-before)<2};});
  if(mobile.pageOverflow||!mobile.scrollable||!mobile.scrolled||!mobile.sticky)throw Error('Mobile matrix issue '+JSON.stringify(mobile));
  await page.evaluate(()=>{document.querySelector('.matrix-scroll').scrollLeft=0});
  await page.locator('#journeyHeat').screenshot({path:'reports/journey_matrix_mobile.png'});
  if(errors.length||remote)throw Error(errors.join('\n')+' requests '+remote);
  console.log(JSON.stringify({matrixFiltersChecked:checked,mobile,errors,remote},null,2));return;
 }
 const options=await page.locator('#deck option').evaluateAll(os=>os.map(o=>o.value));let checked=0;
 for(const v of options){
  await page.selectOption('#deck',v);
  const state=await page.evaluate(()=>{
   const d=+$('deck').value,t=DATA.totals[d];return {cards:document.querySelector('#odds').innerText,name:DATA.names[d],title:document.querySelector('#headline').innerText,entry:t[0],top8:t[1],top4:t[4],top2:t[5],champ:t[6],pathRows:document.querySelectorAll('#examplePaths tbody tr').length};
  });
  if(state.cards.includes('NaN')||!state.title.includes(state.name))throw Error('Invalid deck '+v);
  if(!(state.entry>=state.top8&&state.top8>=state.top4&&state.top4>=state.top2&&state.top2>=state.champ))throw Error('Non-nested placements');checked++;
 }
 await page.selectOption('#deck',String(await page.evaluate(()=>DATA.names.indexOf('Spy Combo'))));
 for(const g of ['all','miss','top8','top4','top2','champ'])for(const o of ['all','0','1','2']){
  await page.selectOption('#group',g);await page.selectOption('#outcome',o);
  const ok=await page.evaluate(()=>{const d=current.deck,gs=current.gs;const n=DATA.paths[d].reduce((a,v)=>a+gs.reduce((b,g)=>b+v[g],0),0);return n===current.gp&&current.jd.every((row,r)=>row.reduce((a,v)=>a+v,0)<=n);});
  if(!ok)throw Error('Wrong journey denominator '+g+' '+o);checked++;
 }
 await page.selectOption('#group','top8');await page.selectOption('#outcome','all');
 for(let r=1;r<=7;r++){
  await page.selectOption('#round',String(r));const options=await page.locator('#record option').evaluateAll(os=>os.map(o=>o.value));
  for(const s of options){await page.selectOption('#record',s);const ok=await page.evaluate(()=>{const d=current.deck,s=current.state,[r,w,l,dr]=states[s];let n=0;for(let c=0;c<2187;c++){let k=c,digits=[];for(let q=0;q<7;q++){digits.unshift(k%3);k=Math.floor(k/3);}if(digits.slice(0,r).filter(v=>v===2).length===w&&digits.slice(0,r).filter(v=>v===1).length===dr)n+=sum(DATA.paths[d][c]);}return n===sum(DATA.exposure[d][s].map(sum));});if(!ok)throw Error('Exact state inconsistency '+s);checked++;}
 }
 await page.selectOption('#round','1');await page.selectOption('#record',String(await page.evaluate(()=>stateId(0,0,0))));
 await page.screenshot({path:'reports/explorer_desktop.png',fullPage:false});await page.setViewportSize({width:390,height:844});await page.waitForTimeout(600);await page.screenshot({path:'reports/explorer_mobile.png',fullPage:false});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2))throw Error('Mobile overflow');
 const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#download').click()]);if(!download.suggestedFilename().endsWith('.csv'))throw Error('CSV failed');
 if(errors.length)throw Error(errors.join('\n'));if(remote)throw Error('Unexpected remote requests');console.log(JSON.stringify({checks:checked,decks:options.length,exactRecords:84,groups:6,results:4,errors,remote,mobile:true,csv:true},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
