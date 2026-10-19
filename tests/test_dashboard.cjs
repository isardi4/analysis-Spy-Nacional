// Functional smoke test in a real local Chrome, including every deck/window.
const {chromium}=require('/private/tmp/spy-browser/node_modules/playwright-core');
const path=require('path');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));let remote=0;
 await page.route('http://**/*',route=>{remote++;return route.abort();});await page.route('https://**/*',route=>{remote++;return route.abort();});
 await page.goto('file://'+path.resolve('reports/legacy_explorer.html'),{waitUntil:'load'});
 await page.waitForFunction(()=>document.querySelectorAll('.js-plotly-plot').length===9);
 const options=await page.locator('#deck option').evaluateAll(os=>os.map(o=>({value:o.value,name:o.textContent})));
 let checked=0;
 for(const opt of options){
  await page.selectOption('#deck',opt.value);
  for(const days of ['30','45']){
   await page.selectOption('#window',days);
   const cards=await page.locator('#cards').innerText();if(cards.includes('NaN')||cards.includes('undefined'))throw Error('Invalid cards '+opt.name);
   const title=await page.locator('#context').innerText();if(!title.includes(opt.name.split(' · ')[0]))throw Error('Stale deck context');
   const state=await page.evaluate(()=>({n:current.d.totals[5],hits:current.d.totals[0],name:DATA.names[current.selected],table:document.querySelectorAll('#matchups tbody tr').length}));
   if(state.n!==100000||state.table!==51)throw Error('Wrong scenario counts');checked++;
  }
 }
 await page.selectOption('#deck',String(await page.evaluate(()=>DATA.names.indexOf('Spy Combo'))));await page.selectOption('#window','30');
 await page.selectOption('#round','6');const ps=await page.locator('#points option').evaluateAll(os=>os.map(o=>o.value));await page.selectOption('#points',ps.at(-1));
 await page.screenshot({path:'reports/legacy_desktop.png',fullPage:false});
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(500);await page.screenshot({path:'reports/legacy_mobile.png',fullPage:false});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+2);
 if(overflow)throw Error('Mobile page overflow');
 if(errors.length)throw Error(errors.join('\n'));if(remote)throw Error('Report requested network '+remote);
 console.log(JSON.stringify({checked,deckOptions:options.length,charts:9,errors,remoteRequests:remote,mobileOverflow:overflow},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
