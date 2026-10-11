import re
t=open('map_tmpl.html').read()
css=open('v245/v245.css').read()
t=t.replace('</style>',css+'\n</style>',1)
t=t.replace('<title>穂波本線 路線図</title>','<title>穂波本線 路線図 v2.4.5</title>')
t=t.replace('<h1>穂波本線 路線図</h1>','<h1>穂波本線 路線図 <span style="font:500 13px var(--mono);color:var(--accent);letter-spacing:.06em;vertical-align:middle">v2.4.5</span></h1>',1)
# panel
a=t.index('<div class="panel" id="p-prof" hidden>');b=t.index('<div class="tbl"><h2 class="hd">区間表</h2>')
newp='''<div class="panel" id="p-prof" hidden>
   <h2 class="hd">縦断面図(路線を選択)</h2><div class="chips" id="plchips"></div>
   <div class="mapbox" id="profbox" style="border:0"><svg id="profsvg" viewBox="0 0 1200 460"></svg></div><div class="pflg" id="proflg"></div><p class="k" id="profnote"></p>
   <h2 class="hd">構造種別の監査</h2><div class="tbl"><table><thead><tr><th>構造種別</th><th>登録数</th><th>3D</th><th>判定</th><th>所見</th></tr></thead><tbody id="saud"></tbody></table></div>
   '''
t=t[:a]+newp+t[b:]
srp='''<div class="panel" id="p-sr" hidden><div class="srbar"><div class="chips" id="srk"></div><div class="srsel"><label class="k" for="srl">路線</label><select id="srl"></select><span class="k" id="srn"></span></div></div>
   <div class="srgrid"><div><div class="srhead" aria-hidden="true"><span>ID</span><span>種別</span><span>名称</span><span>区間</span><span>キロ程</span><span>延長</span><span>3D</span><span>監査</span></div><div id="srb" class="srlist" role="list"></div></div><div id="strd" hidden></div></div></div>
  '''
t=t.replace('<div class="panel" id="p-tb" hidden>',srp+'<div class="panel" id="p-tb" hidden>',1)
# remove old profile code
a=t.index(" var o=NET.order.HM,svg=$('profsvg')");b=t.index(" var kind={寝台:")
t=t[:a]+t[b:]
js=''.join(open('v245/'+f).read()+'\n' for f in ['profile.js','xsec.js','registry.js','company.js'])
js+="profRender('HM');srRender();\n"
m='/* ---------- v2.4: 端末別'
t=t.replace(m,js+m,1)
t=t.replace("['prof','縦断面と区間']];","['prof','縦断面と区間'],['sr','構造物台帳']];")
t=t.replace("['prog','制作状況'],['tb','駅一覧'],['co','会社'],['fl','車両基地・貨物駅'],['th','直通と運行系統'],['sm','種別と停車駅'],['prof','縦断面と区間'],['sr','構造物台帳']","['prog','制作状況'],['tb','駅一覧'],['fl','車両基地・貨物駅'],['sr','構造物台帳'],['prof','縦断面と区間'],['co','会社'],['th','直通と運行系統'],['sm','種別と停車駅']")
assert "['sr'," in t
# p-prof 内の並び: 縦断面 → 区間表 → 線路の接続 → 構造種別の監査
a=t.index('<h2 class="hd">構造種別の監査</h2>');b=t.index('<div class="tbl"><h2 class="hd">区間表</h2>')
aud=t[a:b];t=t[:a]+t[b:]
c=t.index('</tbody></table></div>\n  </div>\n  <div class="panel" id="p-sr"')
t=t[:c]+'</tbody></table></div>\n   '+aud.rstrip()+t[c+len('</tbody></table></div>'):]
open('map_tmpl_v245.html','w').write(t)
print(len(t))
