/* ---------- v2.5: 更新履歴・最新状況 ---------- */
function newsRender(){var N=NET.news,el=$('p-news');if(!N||!el)return;
 var h='<h2 class="hd">更新履歴・最新状況 <span class="tag" style="background:#58b8d0">'+N.version+' / '+N.date+'</span></h2><p class="k">'+N.summary+'</p>';
 if(N.imgs&&N.imgs.length){h+='<div style="display:flex;flex-wrap:wrap;gap:10px;margin:10px 0">'+N.imgs.map(function(m){return '<figure style="margin:0;max-width:440px"><img src="'+m[0]+'" style="width:100%;border-radius:6px"><figcaption class="k">'+m[1]+'</figcaption></figure>'}).join('')+'</div>'}
 N.sections.forEach(function(S){h+='<h3 class="sh">'+S.title+' <span class="tag" style="background:'+(S.state.indexOf('未了')>=0?'#c0783c':(S.state.indexOf('修正済')>=0?'#5ba35b':'#58b8d0'))+'">'+S.state+'</span></h3><ul class="k" style="margin:4px 0 12px 18px;line-height:1.7">'+S.items.map(function(x){return '<li>'+x+'</li>'}).join('')+'</ul>'});
 h+='<p class="k">旧版(v2.1/v2.4.5)は残してあります。穂波野は「駅一覧」「車両基地・貨物駅」タブから詳細を確認できます。</p>';
 el.innerHTML=h}
newsRender();
