"""路線図HTMLの検査: JSエラー・全タブの表示・概念図/実線路図のSVG文字どうし/文字と記号の重なりを数える。
使い方: python3 net/check_map.py net/routemap_v25.html [--shot out_prefix]"""
import glob, sys, json
from playwright.sync_api import sync_playwright
path = sys.argv[1] if len(sys.argv) > 1 else "net/routemap_v25.html"
shot = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None
JS = """
() => {
  const out = [];
  const svgs = [...document.querySelectorAll('svg')].filter(s => s.getBoundingClientRect().width > 300);
  svgs.forEach((svg, si) => {
    const vis = svg.getClientRects().length > 0 && getComputedStyle(svg).visibility !== "hidden";
    if (!vis) return;
    const texts = [...svg.querySelectorAll('text')].filter(t => t.getBoundingClientRect().width > 0 && t.textContent.trim());
    const boxes = texts.map(t => { const r = t.getBoundingClientRect(); return {t: t.textContent.trim().slice(0, 24), x0: r.left, x1: r.right, y0: r.top, y1: r.bottom, cls: t.getAttribute('class') || ''}; });
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      const ox = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), oy = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
      if (ox > 2 && oy > 2) out.push({svg: si, a: a.t, b: b.t, ox: Math.round(ox), oy: Math.round(oy), ax: Math.round(a.x0), ay: Math.round(a.y0)});
    }
    const syms = [...svg.querySelectorAll('circle,rect,polygon')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 3 && r.width < 40 && r.height > 3 && r.height < 40 && e.getClientRects().length; });
    boxes.forEach((a, ai) => syms.forEach(e => {
      if (e.closest('text') || a.t.length <= 1) return;
      const r = e.getBoundingClientRect();
      const ox = Math.min(a.x1, r.right) - Math.max(a.x0, r.left), oy = Math.min(a.y1, r.bottom) - Math.max(a.y0, r.top);
      if (ox > 3 && oy > 3) out.push({svg: si, kind: 'sym', a: a.t, sym: e.tagName, ox: Math.round(ox), oy: Math.round(oy), ax: Math.round(a.x0), ay: Math.round(a.y0)});
    }));
  });
  return out;
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=glob.glob("/opt/pw-browsers/chromium*/chrome-linux*/chrome")[0])
    pg = b.new_page(viewport={"width": 1500, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
    pg.goto("file://" + __import__("os").path.abspath(path)); pg.wait_for_timeout(1500)
    tabs = pg.eval_on_selector_all("#tabs .tab", "els=>els.map(e=>e.id)")
    res = {}
    for t in tabs:
        pg.click("#" + t); pg.wait_for_timeout(400)
        pid = "p-" + t[2:]
        n = pg.eval_on_selector(f"#{pid}", "e=>e.innerText.length")
        res[t] = n
        if shot: pg.screenshot(path=f"{shot}_{t}.png")
    pg.click("#t-prog") if "t-prog" in tabs else None
    pg.wait_for_timeout(400)
    ov = pg.evaluate(JS)
    print("tabs:", res)
    print("errors:", errs[:8])
    print("text overlaps (visible svg):", len(ov))
    for o in ov[:40]: print(" ", o)
    pg.set_viewport_size({"width": 400, "height": 800}); pg.wait_for_timeout(500)
    print("phone-width horizontal overflow px:", pg.evaluate("document.documentElement.scrollWidth - innerWidth"))
    b.close()
