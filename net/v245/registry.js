/* ---------- v2.4.5: 構造物台帳・断面詳細・駅/施設の仕様・監査表 ---------- */
var SA=(NET.struct||{}).audit||{},BUILT={};GEO.links.forEach(function(k){k.items.forEach(function(i){BUILT[i.kind]=(BUILT[i.kind]||0)+1})});
function kauditOf(k){var a=SA[k]||NET.saudit[k];return a||['未監査','']}
function acol(t){return /^不合格/.test(t)?'#e0705a':(/未/.test(t)?'#9bb0a6':'#e5c14b')}
var srK='all',srL='all',srCur=null;
function srRender(){
 var its=STRI.filter(function(s){return (srK==='all'||s.kind===srK)&&(srL==='all'||s.line===srL)});
 var kc={};STRI.forEach(function(s){kc[s.kind]=(kc[s.kind]||0)+1});
 $('srk').innerHTML=['all'].concat(Object.keys(STRK)).filter(function(k){return k==='all'||kc[k]}).map(function(k){return '<button class="chip" data-k="'+k+'" aria-pressed="'+(k===srK)+'">'+(k==='all'?'すべて('+STRI.length+')':'<i style="background:'+STRK[k].color+'"></i>'+STRK[k].name+'('+kc[k]+')')+'</button>'}).join('');
 $('srl').innerHTML='<option value="all">全路線</option>'+Object.keys(NET.lines).map(function(l){return '<option value="'+l+'"'+(l===srL?' selected':'')+'>'+NET.lines[l].name+'</option>'}).join('');
 $('srb').innerHTML=its.map(function(s){var a=kauditOf(s.kind);return '<tr class="frow" data-s="'+s.id+'" tabindex="0"><td class="n">'+s.id+'</td><td><span class="dotk" style="background:'+s.color+'"></span>'+s.kname+'</td><td><b>'+s.name+'</b></td><td>'+NET.lines[s.line].name+'</td><td>'+s.an+' – '+s.bn+'</td><td class="n">'+s.km.toFixed(2)+'</td><td class="n">'+s.len+' m</td><td>'+(BUILT[s.kind]?'<span style="color:#3fcf8e">3D済</span>':'<span style="color:#9bb0a6">データのみ</span>')+'</td><td style="color:'+acol(a[0])+'">'+a[0].replace('(改善中)','')+'</td></tr>'}).join('')||'<tr><td colspan="9">該当なし</td></tr>';
 document.querySelectorAll('#srk .chip').forEach(function(b){b.onclick=function(){srK=b.getAttribute('data-k');srRender()}});
 document.querySelectorAll('#srb .frow').forEach(function(r){var f=function(){strOpen(r.getAttribute('data-s'))};r.onclick=f;r.onkeydown=function(e){if(e.key==='Enter')f()}});
 $('srl').onchange=function(){srL=this.value;srRender()};
 $('srn').textContent=its.length+' 件 ／ 総延長 '+(its.reduce(function(a,s){return a+s.len},0)/1000).toFixed(1)+' km'}
function kvr(a){return '<dl class="kv">'+a.filter(Boolean).map(function(r){return '<dt>'+r[0]+'</dt><dd>'+r[1]+'</dd>'}).join('')+'</dl>'}
function strOpen(id){var s=STRI.filter(function(x){return x.id===id})[0];if(!s)return;srCur=id;var a=kauditOf(s.kind);
 var rows=[['種別',s.kname],['路線',NET.lines[s.line].name],['区間','<a href="#" class="sl" data-s="'+s.a+'">'+s.an+'</a> – <a href="#" class="sl" data-s="'+s.b+'">'+s.bn+'</a>'],['キロ程 / 延長','起点から '+s.km.toFixed(2)+' km ／ '+s.len+' m'],s.form?['形式',s.form]:0,s.year?['竣工',s.year+'年']:0,s.spans?['径間数',s.spans]:0,s.river?['河川',s.river]:0,s.depth?['深さ',s.depth+' m']:0,s.height?['高さ',s.height+' m']:0,s.grade?['勾配',s.grade+' ‰']:0,s.r?['曲線半径','R'+s.r+' m']:0,s.road?['交差道路',s.road]:0,s.vent?['換気塔',s.vent]:0,s.portal?['坑口',s.portal]:0,s.pier?['橋脚',s.pier]:0,s.wire?['架線',s.wire]:0,['3D',BUILT[s.kind]?'制作済(同種 '+BUILT[s.kind]+' 箇所)':'データのみ(未制作)'],['監査','<b style="color:'+acol(a[0])+'">'+a[0]+'</b>']];
 var d=$('strd');d.innerHTML='<h2 class="hd">'+s.id+'　'+s.name+'</h2>'+(s.note?'<p class="k" style="font-family:var(--jp);font-size:12.5px">'+s.note+'</p>':'')+xsecOf(s)+kvr(rows)+'<p class="k">'+(a[1]||'')+'</p>';
 d.hidden=false;d.querySelectorAll('.sl').forEach(function(x){x.onclick=function(e){e.preventDefault();pick(x.getAttribute('data-s'))}});
 document.querySelectorAll('#srb .frow').forEach(function(r){r.classList.toggle('sel',r.getAttribute('data-s')===id)});
 if(MQ_.matches)d.scrollIntoView({behavior:'smooth',block:'start'})}
var MQ_=window.matchMedia('(max-width:900px)');
window.__str=function(id){tab('sr');strOpen(id)};
/* 監査表(構造種別ごと: 登録数/3D/判定/所見) */
$('saud').innerHTML=Object.keys(STRK).map(function(k){var a=kauditOf(k),n=STRI.filter(function(s){return s.kind===k}).length,b=BUILT[k]||0;
 return '<tr><td><span class="dotk" style="background:'+STRK[k].color+'"></span>'+STRK[k].name+'</td><td class="n">'+n+'</td><td class="n">'+(b?'<span style="color:#3fcf8e">済</span>':'<span style="color:#9bb0a6">-</span>')+'</td><td style="color:'+acol(a[0])+';font-weight:700;white-space:nowrap">'+a[0]+'</td><td>'+a[1]+'</td></tr>'}).join('');
/* ---- 駅の設備仕様(設定値) ---- */
var SSP=NET.sspec||{},FSP=NET.fspec||{};
function stationSpec(id){var p=SSP[id];if(!p)return '';var pf=p.platform||{},t=p.ticket||{},sg=p.signal||{},th=p.threed||{};
 var fl=(p.facilities||[]).map(function(f){var o=NET.fac.filter(function(x){return x.id===f})[0];return o?'<a href="#" class="fl" data-f="'+f+'">'+o.name+'</a>':f}).join('、');
 var ns=STRI.filter(function(s){return s.a===id||s.b===id});
 return '<p class="hd" style="margin-top:14px">設備の仕様(設定値)</p>'+kvr([
  ['ホーム',pf.count+'面 '+(pf.form||'')+'／有効長 '+pf.length_m+'m（'+pf.cars+'両）'],['高さ・幅',pf.height_mm+'mm ／ 幅 '+(pf.widths_m||[]).slice(0,3).join('・')+'m'],['屋根・舗装',(pf.roof||'-')+'／'+(pf.surface||'-')],
  ['出札・改札',(t.staff||'-')+'／窓口 '+t.windows+'・改札 '+t.gates+'・券売機 '+t.machines],t.note?['備考',t.note]:0,
  ['信号保安',(sg.block||'-')+'／'+(sg.interlocking||'-')+'／'+(sg.signals||'-')+'／'+(sg.ats||'-')],['電気方式',p.electric||'-'],['構造',p.structure||'-'],
  ['旅客設備',(p.amenities||[]).join('、')||'-'],['駅前',(p.approach||[]).join('、')||'-'],fl?['附帯施設',fl]:0,
  ['3D',(th.shape||'-')+'／画像 '+(th.images||0)+'枚／停車車両 '+(th.stock||'-')],['室内',th.interior||'-'],['監査',th.audit||'-']])
 +(ns.length?'<p class="hd" style="margin-top:10px">接する構造物</p><div class="k" style="font-family:var(--jp);font-size:12.5px;line-height:1.9">'+ns.map(function(s){return '<a href="#" class="ss" data-i="'+s.id+'"><span class="dotk" style="background:'+s.color+'"></span>'+s.name+'</a>'}).join('<br>')+'</div>':'')}
function bindSpec(){var d=$('detail');d.querySelectorAll('a.ss').forEach(function(a){a.onclick=function(e){e.preventDefault();window.__str(a.getAttribute('data-i'))}});
 d.querySelectorAll('a.fl').forEach(function(a){a.onclick=function(e){e.preventDefault();var f=NET.fac.filter(function(x){return x.id===a.getAttribute('data-f')})[0];if(f)pickFac(f)}})}
/* ---- 施設: 配線梯子図と仕様 ---- */
function ladderSvg(l){var n=Math.min(l.tracks||6,24),W=380,H=40+n*11,x0=70,x1=330,g='';
 g+='<line x1="10" y1="'+(H/2)+'" x2="'+x0+'" y2="'+(H/2)+'" stroke="#e4e4e4" stroke-width="2.5"/><text x="10" y="'+(H/2-6)+'" font-size="9.5" style="fill:#9db3a6">本線</text>';
 for(var i=0;i<n;i++){var y=20+i*11;g+='<path d="M'+x0+','+(H/2)+' L'+(x0+14+Math.abs(i-n/2)*1.2)+','+y+' H'+x1+'" stroke="#d8d8d8" stroke-width="1.8" fill="none"/><rect x="'+(x1)+'" y="'+(y-2)+'" width="4" height="4" fill="#d9433f"/>'}
 if(l.shed)g+='<rect x="'+(x0+70)+'" y="14" width="150" height="'+(n*11+8)+'" fill="#8a5b2e" opacity=".28" stroke="#8a5b2e"/><text x="'+(x0+78)+'" y="11" font-size="9.5" style="fill:#c9a27a">検修庫</text>';
 if(l.turntable)g+='<circle cx="'+(x0+10)+'" cy="'+(H/2)+'" r="9" fill="none" stroke="#e8c868" stroke-width="2"/><text x="'+(x0-4)+'" y="'+(H-2)+'" font-size="9.5" style="fill:#e8c868">転車台</text>';
 return '<svg viewBox="0 0 '+W+' '+H+'" class="sch" role="img" aria-label="配線梯子図"><rect width="'+W+'" height="'+H+'" fill="#0f2219"/>'+g+'<text x="'+(W-6)+'" y="'+(H-3)+'" text-anchor="end" font-size="9.5" style="fill:#9db3a6">留置・検修線 '+n+'線</text></svg>'}
function facSpec(f){var p=FSP[f.id];if(!p)return '';return '<p class="hd" style="margin-top:14px">施設の仕様(設定値)</p>'+kvr([['収容',p.capacity],['要員',p.staff+'人'],['稼働',p.hours],['電力',p.power],['建物',(p.buildings||[]).join('、')||'-'],['3D',p.three_d]])+(p.ladder?'<p class="hd">配線(概念)</p>'+ladderSvg(p.ladder):'')}
var _pk=pick,_pf=pickFac;
pick=function(id){_pk(id);$('detail').insertAdjacentHTML('beforeend',stationSpec(id));bindSpec()};
pickFac=function(f){_pf(f);$('detail').insertAdjacentHTML('beforeend',facSpec(f));bindSpec()};
