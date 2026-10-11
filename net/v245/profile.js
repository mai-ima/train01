/* ---------- v2.4.5: 路線別 縦断面図(キロ程・標高・勾配‰・構造物帯) ---------- */
var PLN='HM',STRK=(NET.struct||{}).kinds||{},STRI=(NET.struct||{}).items||[];
var LANE={subway:0,tunnel:0,shed:0,street:0,viaduct:1,truss:1,arch:1,trestle:1,mono:1,over:1,sea:1,embank:2,cut:2,lc:2,curve:2,turnout:2,snowfence:2};
var LANEN=['地下・トンネル・覆い','橋・高架','土工・平面構造'];
function lkm(l,i){var o=NET.order[l];return o.indexOf(i)===0?0:S[i].km}
function profRender(l){
 if(l)PLN=l;var o=NET.order[PLN],svg=$('profsvg'),W=1200,L=124,R=24,T=34,GB=156,BH=3*20+30;
 var es=o.map(function(i){return S[i].elev}),emax=Math.max.apply(0,es),emin=Math.min.apply(0,es);
 var top=Math.max(10,Math.ceil((emax+(emax-emin)*.1+6)/ (emax>150?50:10))*(emax>150?50:10)),bot=emin<0?Math.floor((emin-8)/10)*10:0;
 var step=(top-bot)>300?100:((top-bot)>100?50:((top-bot)>40?20:10));
 var km=o.map(function(i){return lkm(PLN,i)});var maxk=Math.max(km[km.length-1],.5);
 var PH=290,H=T+PH+GB+BH;
 function X(k){return L+(W-L-R)*k/maxk}function Y(e){return T+PH*(1-(e-bot)/(top-bot))}
 var h='<defs><pattern id="pfh" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#355f4b" stroke-width="1"/></pattern></defs>';
 for(var e=Math.ceil(bot/step)*step;e<=top;e+=step)h+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+Y(e)+'" y2="'+Y(e)+'" stroke="'+(e===0?'#5f9d82':'#1f3a2f')+'" stroke-dasharray="'+(e===0?'6 4':'0')+'"/><text x="'+(L-8)+'" y="'+(Y(e)+4)+'" text-anchor="end" font-size="11" style="fill:#7f9a8c">'+e+' m</text>';
 if(bot<0)h+='<rect x="'+L+'" y="'+Y(0)+'" width="'+(W-L-R)+'" height="'+(Y(bot)-Y(0))+'" fill="#2a2018" opacity=".55"/><text x="'+(W-R-4)+'" y="'+(Y(0)+14)+'" text-anchor="end" font-size="10" style="fill:#c9a27a">地下(地表より下)</text>';
 for(var t=0;t<=maxk+.001;t+= (maxk>40?10:(maxk>14?2:1)))h+='<line x1="'+X(t)+'" x2="'+X(t)+'" y1="'+T+'" y2="'+(T+PH)+'" stroke="#1a3329"/><text x="'+X(t)+'" y="'+(T+PH+13)+'" text-anchor="middle" font-size="10" style="fill:#6f8a7c">'+t+'km</text>';
 var pts=o.map(function(i,n){return X(km[n])+','+Y(S[i].elev)}).join(' ');
 h+='<polygon points="'+X(0)+','+Y(bot)+' '+pts+' '+X(km[km.length-1])+','+Y(bot)+'" fill="url(#pfh)" opacity=".9"/>';
 /* 構造物(線上) */
 var its=STRI.filter(function(s){return s.line===PLN});
 function eAt(k){for(var n=0;n<o.length-1;n++){if(k>=km[n]-.001&&k<=km[n+1]+.001){var f=(k-km[n])/Math.max(km[n+1]-km[n],.01);return S[o[n]].elev+(S[o[n+1]].elev-S[o[n]].elev)*f}}return S[o[o.length-1]].elev}
 its.forEach(function(s){var k0=s.km,k1=s.km+s.len/1000,col=s.color||'#999';if(k1>maxk)k1=maxk;var x0=X(k0),x1=Math.max(x0+5,X(k1)),y0=Y(eAt(k0)),y1=Y(eAt(k1));
  if(s.kind==='subway'||s.kind==='tunnel'||s.kind==='shed')h+='<polyline points="'+x0+','+y0+' '+x1+','+y1+'" stroke="'+col+'" stroke-width="12" opacity=".35" fill="none" stroke-linecap="round"/>';
  else if(s.kind==='viaduct'||s.kind==='truss'||s.kind==='arch'||s.kind==='trestle'||s.kind==='mono'||s.kind==='sea'){var n=Math.max(2,Math.round((x1-x0)/16));for(var q=0;q<=n;q++){var xx=x0+(x1-x0)*q/n,yy=y0+(y1-y0)*q/n;h+='<line x1="'+xx+'" x2="'+xx+'" y1="'+yy+'" y2="'+(yy+16)+'" stroke="'+col+'" stroke-width="2"/>'}}
  else if(s.kind==='embank')h+='<polyline points="'+x0+','+(y0-0)+' '+x1+','+y1+'" stroke="'+col+'" stroke-width="7" opacity=".5" fill="none"/>';
  else if(s.kind==='cut')h+='<polyline points="'+x0+','+(y0+5)+' '+x1+','+(y1+5)+'" stroke="'+col+'" stroke-width="5" opacity=".7" fill="none" stroke-dasharray="5 3"/>'});
 h+='<polyline points="'+pts+'" fill="none" stroke="'+NET.lines[PLN].color+'" stroke-width="3.5" stroke-linejoin="round"/>';
 /* 勾配‰(プロット下の専用帯。重なる場合は間引く) */
 h+='<text x="'+(L-8)+'" y="'+(T+PH+33)+'" text-anchor="end" font-size="9.5" style="fill:#6f8a7c">勾配</text>';var gr=-99;
 for(var n=0;n<o.length-1;n++){var dk=(km[n+1]-km[n])*1000;if(dk<=0)continue;var g=(S[o[n+1]].elev-S[o[n]].elev)/dk*1000,xm=X((km[n]+km[n+1])/2);
  if(Math.abs(g)<0.5||xm-24<gr)continue;gr=xm+24;var up=g>0;h+='<text x="'+xm+'" y="'+(T+PH+33)+'" text-anchor="middle" font-size="10.5" style="fill:'+(Math.abs(g)>=25?'#ff9a6b':'#cfe0d6')+';font-family:var(--mono)">'+(up?'▲':'▼')+Math.abs(g).toFixed(1)+'‰</text>'}
 /* 駅 */
 var lastx=-99,row=0,lx2=-99,stg=0;
 o.forEach(function(i,n){var s=S[i],x=X(km[n]),y=Y(s.elev);h+='<line x1="'+x+'" x2="'+x+'" y1="'+y+'" y2="'+(T+PH)+'" stroke="#2f5545" stroke-dasharray="2 3"/><circle cx="'+x+'" cy="'+y+'" r="5" fill="#fff" stroke="#0e1f19" stroke-width="2" style="cursor:pointer" onclick="window.__pick(\''+i+'\')"/>';
  h+='<text x="'+x+'" y="'+(y-10-(x-lastx<42?11:0))+'" text-anchor="middle" font-size="10" style="fill:#e8c868;font-family:var(--mono)">'+s.elev+'</text>';lastx=x;
  h+='<text transform="translate('+(x+4)+','+(T+PH+44)+') rotate(90)" font-size="11" style="fill:#cfe0d6;cursor:pointer" onclick="window.__pick(\''+i+'\')">'+s.name+'</text>'});
 /* 構造物帯(3レーン) */
 var by=T+PH+GB;LANEN.forEach(function(nm,ln){h+='<text x="'+(L-8)+'" y="'+(by+ln*20+13)+'" text-anchor="end" font-size="9.5" style="fill:#6f8a7c">'+nm+'</text><line x1="'+L+'" x2="'+(W-R)+'" y1="'+(by+ln*20+19)+'" y2="'+(by+ln*20+19)+'" stroke="#1a3329"/>'});
 its.forEach(function(s){var ln=LANE[s.kind]||0,x0=X(s.km),w=Math.max(8,X(s.km+s.len/1000)-x0);h+='<g style="cursor:pointer" onclick="window.__str(\''+s.id+'\')"><rect x="'+x0+'" y="'+(by+ln*20+3)+'" width="'+w+'" height="14" rx="2" fill="'+s.color+'" opacity=".92"/><title>'+s.name+' '+s.len+'m</title></g>'});
 svg.setAttribute('viewBox','0 0 '+W+' '+H);svg.innerHTML=h;
 var used={};its.forEach(function(s){used[s.kind]=1});
 $('proflg').innerHTML=Object.keys(used).map(function(k){return '<span><i style="background:'+STRK[k].color+'"></i>'+STRK[k].name+'</span>'}).join('')||'<span>この路線に登録された構造物はありません</span>';
 $('profnote').innerHTML=NET.lines[PLN].name+'：キロ程 '+maxk.toFixed(1)+' km、最高 '+emax+' m／最低 '+emin+' m。数値は駅の軌条面標高(m)。駅間の ▲▼ は平均勾配(‰)で、25‰以上は橙。構造物帯の帯をクリックすると詳細と断面図が開きます。';
 document.querySelectorAll('#plchips .chip').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-l')===PLN?'true':'false')})}
(function(){var c=$('plchips');Object.keys(NET.order).forEach(function(l){var b=document.createElement('button');b.className='chip';b.setAttribute('data-l',l);b.setAttribute('aria-pressed','false');b.innerHTML='<i style="background:'+NET.lines[l].color+'"></i>'+NET.lines[l].name;b.onclick=function(){profRender(l)};c.appendChild(b)})})();
window.__pick=function(i){pick(i)};
