/* ---------- v2.4.5: 会社の詳細・運行系統・直通運転(既存情報はすべて残して見やすく再構成) ---------- */
var KC={寝台:'#4a3f8f',特急:'#d9433f',急行:'#e8962a',区間急行:'#f0b43c',ライナー:'#14a3a8',快速:'#c8a22b',普通:'#2f9e6b',直通:'#3b7bd9',貨物:'#8a8f94',臨時:'#c06bd0',回送:'#6b7280',試運転:'#b0b6bd'};
var KRANK=['寝台','特急','急行','区間急行','ライナー','快速','普通','直通','臨時','回送','試運転','貨物'];
function pairKm(a,b){var best=0;Object.keys(NET.order).forEach(function(l){var o=NET.order[l],ia=o.indexOf(a),ib=o.indexOf(b);if(ia>=0&&ib>=0&&Math.abs(ia-ib)===1&&!best)best=Math.abs(lkm(l,a)-lkm(l,b))});if(best)return best;var t=0;GEO.links.forEach(function(k){if(k.k>0)return;if((k.a===a&&k.b===b)||(k.a===b&&k.b===a))t+=k.len});return t/1000}
function pathKm(P){var t=0;for(var i=0;i<P.length-1;i++)t+=pairKm(P[i],P[i+1]);return t}
function stLink(i){return '<a href="#" class="sl" data-s="'+i+'">'+S[i].name+'</a>'}
function spark(P,stops,col){var n=P.length,W=Math.max(300,Math.min(n*22,900)),dx=n>1?(W-24)/(n-1):0,g='<line x1="12" x2="'+(W-12)+'" y1="14" y2="14" stroke="'+col+'" stroke-width="2.5" opacity=".55"/>';
 P.forEach(function(i,k){var st=!stops||stops.indexOf(i)>=0,x=12+dx*k;g+='<circle cx="'+x+'" cy="14" r="'+(st?4.6:2.4)+'" fill="'+(st?col:'#0e1f19')+'" stroke="'+col+'" stroke-width="1.4"><title>'+S[i].name+(st?'(停車)':'(通過)')+'</title></circle>'});
 g+='<text x="12" y="31" font-size="10" style="fill:#9db3a6">'+S[P[0]].name+'</text><text x="'+(W-12)+'" y="31" text-anchor="end" font-size="10" style="fill:#9db3a6">'+S[P[n-1]].name+'</text>';
 return '<div class="spk"><svg viewBox="0 0 '+W+' 36" style="min-width:'+Math.min(W,300)+'px;width:100%;height:auto" role="img" aria-label="停車駅図">'+g+'</svg></div>'}
function elecOf(secs){var o=[];(NET.elec||[]).forEach(function(e){var a=NET.order[e.line];if(!a)return;var ia=a.indexOf(e.a),ib=a.indexOf(e.b);if(ia<0||ib<0)return;var lo=Math.min(ia,ib),hi=Math.max(ia,ib);if(secs.filter(function(i){var k=a.indexOf(i);return k>=lo&&k<=hi}).length>=2)o.push(NET.lines[e.line].name+': '+e.sys)});return o.filter(function(v,i,a){return a.indexOf(v)===i})}
function tile(n,l){return '<div class="tile"><b>'+n+'</b><span>'+l+'</span></div>'}
/* --- 会社 --- */
showCo=function(id){var C=NET.companies[id];document.querySelectorAll('#cotabs button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-co')===id?'true':'false')});
 var ls=Object.keys(NET.lines).filter(function(l){return NET.lines[l].co===id});
 var sts=NET.stations.filter(function(s){return s.lines.some(function(l){return NET.lines[l].co===id})});
 var th=NET.through.filter(function(t){return NET.lines[t.from].co===id||NET.lines[t.onto].co===id});
 var fc=(NET.fac||[]).filter(function(f){return f.co===id});
 var sv=NET.svc.filter(function(v){return v[3]===id}).sort(function(a,b){return KRANK.indexOf(a[2])-KRANK.indexOf(b[2])});
 var si=STRI.filter(function(s){return NET.lines[s.line].co===id});
 var km=0,real=0;ls.forEach(function(l){var o=NET.order[l];km+=Math.abs(S[o[o.length-1]].km-(o.length>1&&l!=='HM'&&l!=='KE'&&l!=='KM'?0:S[o[0]].km));real+=GEO.links.filter(function(k){return k.line===l&&!(k.k>0)}).reduce(function(a,k){return a+k.len},0)});
 var xf=sts.filter(function(s){return s.lines.some(function(l){return NET.lines[l].co!==id})});
 var h='<div class="cohead" style="border-left:6px solid '+C.color+'"><b class="conm">'+C.name+'</b><p class="k cinfo">'+(C.info||'')+'</p></div>';
 h+='<div class="tiles">'+tile(ls.length,'路線')+tile(sts.length,'駅')+tile(real?(real/1000).toFixed(1):'-','実線路km(駅間)')+tile(si.length,'構造物')+tile(fc.length,'車庫・ヤード')+tile(sv.length,'運行系統')+tile(th.length,'直通')+'</div>';
 h+='<dl class="kv wide"><dt>本社</dt><dd>'+(C.hq||'-')+'</dd><dt>開業</dt><dd>'+(C.founded||'-')+'</dd><dt>軌間</dt><dd>'+(C.gauge||'-')+'</dd><dt>電源</dt><dd>'+(C.power||'-')+'</dd><dt>主な車両</dt><dd>'+(C.fleet||[]).join('・')+'</dd><dt>駅('+sts.length+')</dt><dd>'+sts.map(function(s){return stLink(s.id)}).join('・')+'</dd>'+(xf.length?'<dt>他社との接点</dt><dd>'+xf.map(function(s){return stLink(s.id)+'<span class="k">('+s.lines.map(function(l){return NET.lines[l].co===id?'':NET.companies[NET.lines[l].co].name}).filter(Boolean).join('・')+')</span>'}).join('・')+'</dd>':'')+'</dl>';
 h+='<h3 class="sh">路線</h3>'+ls.map(function(l){var o=NET.order[l],len=(S[o[o.length-1]].km-S[o[0]].km).toFixed(1);var lk=GEO.links.filter(function(k){return k.line===l});var tot=lk.reduce(function(a,k){return a+(k.k>0?0:k.len)},0);var ni=STRI.filter(function(s){return s.line===l}).length;
  return '<details class="ln" style="border-left:4px solid '+NET.lines[l].color+'"><summary><b>'+NET.lines[l].name+'</b> <span class="k">'+NET.lines[l].kind+'<br>'+len+'km ／ '+o.length+'駅 ／ 実線路 '+(tot/1000).toFixed(2)+'km(駅間) ／ 構造物 '+ni+'件</span></summary>'+spark(o,null,NET.lines[l].color)+'<div class="k" style="line-height:1.9">'+o.map(function(i){return stLink(i)+' <span style="color:#7f9a8c">'+S[i].km.toFixed(1)+'k/'+S[i].elev+'m</span>'}).join(' — ')+'</div></details>'}).join('');
 if(sv.length)h+='<h3 class="sh">運行系統('+sv.length+')</h3><div class="svg">'+sv.map(function(v){var c=KC[v[2]]||'#999';return '<div class="svc1" style="border-left:5px solid '+c+'"><b>'+v[1]+'</b> <span class="tag" style="background:'+c+'">'+v[2]+'</span> <span class="k">'+v[5]+' ／ 所要約'+v[6]+'分</span></div>'}).join('')+'</div>';
 if(th.length)h+='<h3 class="sh">直通運転</h3>'+th.map(function(t){return '<div class="svc1" style="border-left:5px solid '+NET.lines[t.from].color+'"><b>'+t.name+'</b><div class="k">'+t.section.map(function(i){return S[i].name}).join(' → ')+'(区間 約'+pathKm(t.section).toFixed(1)+'km)</div></div>'}).join('');
 else if(id!=='JNR')h+='<h3 class="sh">直通運転</h3><p class="k">直通・乗入れなし(他社)。駅は国鉄駅に隣接するが線路は接続しない。</p>';
 var kc={};si.forEach(function(s){kc[s.kind]=(kc[s.kind]||0)+1});
 if(si.length)h+='<h3 class="sh">構造物('+si.length+')</h3><div class="chips">'+Object.keys(kc).map(function(k){return '<button class="chip" data-sk="'+k+'" aria-pressed="true"><i style="background:'+STRK[k].color+'"></i>'+STRK[k].name+'('+kc[k]+')</button>'}).join('')+'</div>';
 if(fc.length)h+='<h3 class="sh">車庫・ヤード('+fc.length+')</h3>'+fc.map(function(f){return '<div class="svc1" style="border-left:5px solid '+C.color+'"><a href="#" class="fl2" data-f="'+f.id+'"><b>'+f.name+'</b></a> <span class="k">('+f.desc+')</span></div>'}).join('');
 $('codetail').innerHTML=h;var d=$('codetail');
 d.querySelectorAll('.sl').forEach(function(a){a.onclick=function(e){e.preventDefault();pick(a.getAttribute('data-s'));window.scrollTo({top:0,behavior:'smooth'})}});
 d.querySelectorAll('.fl2').forEach(function(a){a.onclick=function(e){e.preventDefault();var f=NET.fac.filter(function(x){return x.id===a.getAttribute('data-f')})[0];if(f){pickFac(f);window.scrollTo({top:0,behavior:'smooth'})}}});
 d.querySelectorAll('[data-sk]').forEach(function(b){b.onclick=function(){srK=b.getAttribute('data-sk');srL=si[0].line;srL='all';tab('sr');srRender()}})};
/* --- 運行系統 --- */
var svCo='all',svK='all';
function svrender2(){var rows=NET.svc.slice().sort(function(a,b){return KRANK.indexOf(a[2])-KRANK.indexOf(b[2])}).filter(function(v){return (svK==='all'||v[2]===svK)&&(svCo==='all'||v[3]===svCo)});
 var kc={};NET.svc.forEach(function(v){kc[v[2]]=(kc[v[2]]||0)+1});
 var chips='<div class="chips" id="svchips">'+['all'].concat(KRANK).filter(function(k){return k==='all'||kc[k]}).map(function(k){return '<button class="chip" data-k="'+k+'" aria-pressed="'+(k===svK)+'">'+(k==='all'?'すべて('+NET.svc.length+')':'<i style="background:'+KC[k]+'"></i>'+k+'('+kc[k]+')')+'</button>'}).join('')+'</div><div class="chips" id="svco"><span class="k">会社</span>'+['all'].concat(Object.keys(NET.companies)).map(function(c){return '<button class="chip" data-c="'+c+'" aria-pressed="'+(c===svCo)+'">'+(c==='all'?'全社':NET.companies[c].name)+'</button>'}).join('')+'</div><p class="k">'+rows.length+' 系統を表示</p>';
 $('svclist').innerHTML=chips+rows.map(function(v){var c=KC[v[2]]||'#999',P=v[9]||v[4],km=pathKm(P);
  return '<article class="svcard" style="border-left:6px solid '+c+'"><header><b>'+v[1]+'</b> <span class="tag" style="background:'+c+'">'+v[2]+'</span> <span class="k">'+NET.companies[v[3]].name+'</span></header>'
  +'<dl class="kv wide"><dt>運転区間</dt><dd>'+stLink(P[0])+' → '+stLink(P[P.length-1])+(km?'(約'+km.toFixed(1)+'km)':'')+'</dd><dt>本数・所要</dt><dd>'+v[5]+' ／ 所要約'+v[6]+'分</dd><dt>停車</dt><dd>'+v[4].length+'駅停車／'+P.length+'駅中'+(P.length-v[4].length>0?'(通過'+(P.length-v[4].length)+')':'')+'</dd><dt>使用車両</dt><dd>'+v[7]+'</dd></dl>'
  +spark(P,v[4],c)+'<details class="stl"><summary class="k">停車駅の一覧</summary><div class="k" style="line-height:1.9">'+P.map(function(i){var st=v[4].indexOf(i)>=0;return st?'<b style="color:'+c+'">●'+S[i].name+'</b>':'<span style="opacity:.5">｜'+S[i].name+'(通過)</span>'}).join(' → ')+'</div></details><p class="k note">'+v[8]+'</p></article>'}).join('');
 var d=$('svclist');d.querySelectorAll('#svchips .chip').forEach(function(b){b.onclick=function(){svK=b.getAttribute('data-k');svrender2()}});d.querySelectorAll('#svco .chip').forEach(function(b){b.onclick=function(){svCo=b.getAttribute('data-c');svrender2()}});
 d.querySelectorAll('.sl').forEach(function(a){a.onclick=function(e){e.preventDefault();pick(a.getAttribute('data-s'));window.scrollTo({top:0,behavior:'smooth'})}})}
/* --- 直通運転 --- */
function threnderer(){$('th').innerHTML='';NET.through.forEach(function(t){var f=NET.lines[t.from],o=NET.lines[t.onto],A=NET.companies[f.co],B=NET.companies[o.co],km=pathKm(t.section);
  var rel=NET.svc.filter(function(v){var P=v[9]||v[4];return (v[3]===f.co||v[3]===o.co)&&t.section.filter(function(i){return P.indexOf(i)>=0}).length>=Math.min(2,t.section.length)&&(v[2]==='直通'||v[7].indexOf('直通')>=0||v[1].indexOf('直通')>=0)});
  var ns=STRI.filter(function(s){return (s.line===t.from||s.line===t.onto)&&t.section.indexOf(s.a)>=0&&t.section.indexOf(s.b)>=0});var el=elecOf(t.section);
  var d=document.createElement('article');d.className='thcard';d.style.borderLeftColor=f.color;
  d.innerHTML='<header><b>'+t.name+'</b></header><div class="k thco"><span style="color:'+A.color+'">■</span> '+A.name+' → <span style="color:'+B.color+'">■</span> '+B.name+'(線路: '+f.name+' → '+o.name+')</div>'+spark(t.section,null,f.color)
  +'<dl class="kv wide"><dt>区間</dt><dd>'+t.section.map(stLink).join(' → ')+(km?'(約'+km.toFixed(1)+'km)':'')+'</dd><dt>使用車両</dt><dd>'+t.stock+'</dd>'+(el.length?'<dt>電化</dt><dd>'+el.join('／')+'</dd>':'')+(rel.length?'<dt>関連系統</dt><dd>'+rel.map(function(v){return v[1]+'('+v[2]+')'}).join('・')+'</dd>':'')+(ns.length?'<dt>区間の構造物</dt><dd>'+ns.map(function(s){return '<a href="#" class="ss" data-i="'+s.id+'">'+s.name+'</a>'}).join('・')+'</dd>':'')+'</dl><p class="k note">'+t.note+'</p>';
  $('th').appendChild(d)});
 $('th').querySelectorAll('.sl').forEach(function(a){a.onclick=function(e){e.preventDefault();pick(a.getAttribute('data-s'));window.scrollTo({top:0,behavior:'smooth'})}});
 $('th').querySelectorAll('a.ss').forEach(function(a){a.onclick=function(e){e.preventDefault();window.__str(a.getAttribute('data-i'))}})}
svrender2();threnderer();showCo('JNR');
