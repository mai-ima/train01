/* ---------- 周遊列車「結」(不定期高級周遊列車・3泊4日) ---------- */
function tourRender(){var T=NET.tour,el=$('p-tour');if(!T||!el)return;
 var col=['#e89a3c','#58b8d0','#8fd16d','#e66d95'];
 var h='<h2 class="hd">'+T.name+'(ゆい) 不定期高級周遊列車</h2>';
 h+='<div class="tiles">'+tile(T.days+'日間・'+T.nights+'泊','日程')+tile(T.consist.length+'両','編成')+tile(T.rooms+'室/'+T.capacity+'名','客室/定員')+tile(T.kind,'種別(既存)')+'</div>';
 h+='<dl class="kv wide"><dt>運行</dt><dd>'+T.season+'</dd><dt>予約</dt><dd>'+T.booking+'</dd><dt>動力</dt><dd>'+T.traction+'</dd><dt>塗色</dt><dd>'+T.livery+'</dd></dl>';
 if(T.imgs&&T.imgs.length){h+='<div class="tourimgs" style="display:flex;flex-wrap:wrap;gap:10px;margin:10px 0">'+T.imgs.map(function(m){return '<figure style="margin:0;max-width:'+(m[0].length>200000?'460':'220')+'px;flex:1 1 200px"><img src="'+m[0]+'" alt="'+m[1]+'" style="width:100%;height:auto;border-radius:6px"><figcaption class="k">'+m[1]+'</figcaption></figure>'}).join('')+'</div>'}
 h+='<p class="k">'+T.rooms_note+'</p>';
 h+='<h3 class="sh">日程と経路(本線と各支線を周遊)</h3>';
 T.legs.forEach(function(L,i){var sv=NET.svc.filter(function(v){return v[0]===L.svc})[0];if(!sv)return;var P=sv[9]||sv[4];
  h+='<div class="svc1" style="border-left:6px solid '+col[i]+'"><b>'+L.day+'日目 '+S[L.from].name+' → '+S[L.to].name+'</b> <span class="tag" style="background:'+(KC[sv[2]]||'#c06bd0')+'">'+sv[2]+'</span> <span class="k">'+sv[0]+' ／ 所要'+sv[6]+'分 ／ 停車'+sv[4].length+'駅</span>'+'<div style="max-width:560px">'+spark(P,sv[4],col[i])+'</div>'+
   '<div class="k">停車: '+sv[4].map(function(x){return stLink(x)}).join(' → ')+'<br>'+L.spots.join('<br>')+'<br>滞在: '+L.stay+'<br>宿泊: '+L.night_note+'</div><button class="chip tour-hl" data-svc="'+L.svc+'">この日の経路を地図で強調</button></div>'});
 h+='<h3 class="sh">編成(10両・ハイブリッド自走)</h3><div class="tbl"><table><thead><tr><th>号車</th><th>形式</th><th>名称</th><th>内容</th></tr></thead><tbody>'+T.consist.map(function(c){return '<tr><td>'+c[0]+'</td><td>'+c[1]+'</td><td>'+c[2]+'</td><td>'+c[3]+'</td></tr>'}).join('')+'</tbody></table></div>';
 h+='<p class="k">参考にした実在の周遊列車の運行形態・編成の考え方は net/research_tour.md に出典つきで記録。車両・ヘッドマーク・行先表示は原作オリジナル(ヘッドマークは未装着)。種別は既存の「臨時」。</p>';
 el.innerHTML=h;
 el.querySelectorAll('.tour-hl').forEach(function(b){b.onclick=function(){var sel=$('svsel');sel.value=b.getAttribute('data-svc');sel.dispatchEvent(new Event('change'));window.scrollTo({top:0,behavior:'smooth'})}});
 el.querySelectorAll('.sl').forEach(function(a){a.onclick=function(e){e.preventDefault();pick(a.getAttribute('data-s'));window.scrollTo({top:0,behavior:'smooth'})}})}
tourRender();
