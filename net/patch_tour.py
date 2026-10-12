"""map_tmpl_v245.html に「周遊列車」タブとパネルを追加する(冪等)。"""
t = open("map_tmpl_v245.html").read()
if 'id="p-tour"' not in t:
    t = t.replace('<div class="panel" id="p-tb" hidden>', '<div class="panel" id="p-tour" hidden></div>\n  <div class="panel" id="p-tb" hidden>', 1)
if "['tour'," not in t:
    assert "['th','直通と運行系統']" in t
    t = t.replace("['th','直通と運行系統']", "['th','直通と運行系統'],['tour','周遊列車「結」']", 1)
import re
js = open("v245/tour.js").read()
if "function tourRender" in t:
    a = t.index("/* ---------- 周遊列車「結」")
    b = t.index("tourRender();", a) + len("tourRender();")
    t = t[:a] + js.rstrip() + t[b:]
else:
    m = '/* ---------- v2.4: 端末別'
    assert m in t
    t = t.replace(m, js + "\n" + m, 1)
open("map_tmpl_v245.html", "w").write(t)
print("patched", len(t))
