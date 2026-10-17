"""map_tmpl_v245.html を元に map_tmpl_v25.html を作る(冪等・毎回作り直し)。版表記の更新+『更新履歴』タブの追加。"""
t = open("map_tmpl_v245.html").read()
t = t.replace('<title>穂波本線 路線図 v2.4.5</title>', '<title>穂波本線 路線図 v2.5</title>')
t = t.replace('letter-spacing:.06em;vertical-align:middle">v2.4.5</span>', 'letter-spacing:.06em;vertical-align:middle">v2.5</span>')
assert 'id="p-news"' not in t
t = t.replace('<div class="panel" id="p-prog">', '<div class="panel" id="p-news"></div>\n  <div class="panel" id="p-prog" hidden>', 1)
assert "var TABS=[['prog','制作状況']" in t
t = t.replace("var TABS=[['prog','制作状況']", "var TABS=[['news','更新履歴・最新状況'],['prog','制作状況']", 1)
t = t.replace("t[0]==='prog'?'true'", "t[0]==='news'?'true'", 1)
js = open("v25/news.js").read()
m = '/* ---------- v2.4: 端末別'
assert m in t
t = t.replace(m, js + "\n" + m, 1)
open("map_tmpl_v25.html", "w").write(t)
print("v2.5 template", len(t))
