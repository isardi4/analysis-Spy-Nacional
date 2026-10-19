/* Match-level decisive WR. Wilson intervals use observations, never simulations. */
function wilson95(w,l){
 const n=w+l;if(!n)return null;
 const z=1.959963984540054,p=w/n,z2=z*z,den=1+z2/n,center=(p+z2/(2*n))/den,half=z*Math.sqrt(p*(1-p)/n+z2/(4*n*n))/den;
 return [Math.max(0,center-half),Math.min(1,center+half)];
}
function matchupStats(W,D,a,b,sources=[0,1]){
 const mirror=a===b,w=sources.reduce((n,q)=>n+W[q][a][b],0),l=mirror?null:sources.reduce((n,q)=>n+W[q][b][a],0),d=sources.reduce((n,q)=>n+D[q][a][b],0)/(mirror?2:1),n=mirror?w:w+l,total=n+d;
 const alpha=w+5,beta=(l===null?w:l)+5,den=alpha+beta;
 return {mirror,w:mirror?null:w,l,d,n,total,observed:mirror?null:(n?w/n:null),ci:mirror?null:wilson95(w,l),adjusted:mirror?.5:alpha/den,posteriorSD:mirror?null:Math.sqrt(alpha*beta/(den*den*(den+1)))};
}
if(typeof module!=='undefined')module.exports={wilson95,matchupStats};
