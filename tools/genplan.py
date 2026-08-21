# -*- coding: utf-8 -*-
"""Генератор SVG-плана квартиры для index.html.

Координаты в сантиметрах, начало отсчёта — наружный левый верхний угол балкона.
Геометрия помещений и проёмов восстановлена из векторного плана попиксельно и
сверена с экспликацией БТИ (сумма площадей 43,5 м² против 43,6 в паспорте).

Запуск: python3 tools/genplan.py            — печатает SVG в stdout
        python3 tools/genplan.py --preview  — пишет tools/plan-preview.html
"""
import sys

# --- помещения: id, имя, площадь, контур, точка подписи -----------------------
ROOMS = [
    ("k2",   "Комната",  "17,1", [(0,209),(307,209),(307,767),(0,767)],     (153, 470)),
    ("k3",   "Комната",  "10,5", [(320,26),(568,26),(568,448),(320,448)],   (444, 210)),
    ("kit",  "Кухня",    "6,9",  [(581,26),(800,26),(800,242),(812,242),
                                  (812,319),(581,319)],                      (688, 150)),
    ("hall", "Прихожая", "3,4",  [(320,460),(568,460),(568,594),(320,594)], (430, 512)),
    ("cor",  "Коридор",  "1,8",  [(583,334),(673,334),(673,596),(583,596)], (628, 450)),
    ("wc",   "Туалет",   "0,9",  [(683,332),(813,332),(813,402),(683,402)], (748, 360)),
    ("bath", "Ванная",   "2,3",  [(683,412),(813,412),(813,592),(683,592)], (748, 490)),
]
BALCONY = [(0,0),(263,0),(263,148),(0,148)]
SHELL   = [(-14,195),(306,195),(306,12),(827,12),(827,606),(321,606),(321,782),(-14,782)]

# --- проёмы: x0,y0,x1,y1, вид, подпись, точность ------------------------------
# вид: door | opening | window | entrance
# точность: True — снято с плана, False — реконструкция, требует замера
OPENINGS = [
    (154, 148, 243, 209, "door",     "89",  True),   # балконная дверь
    (307, 464, 320, 553, "door",     "89",  True),   # в комнату 17,1
    (474, 448, 563, 460, "door",     "89",  True),   # в комнату 10,5
    (581, 319, 670, 334, "door",     "89",  True),   # на кухню
    (673, 334, 683, 402, "door",     "68",  True),   # в туалет
    (673, 468, 683, 531, "door",     "63",  True),   # в ванную
    (568, 460, 583, 592, "opening",  "132", True),   # прихожая — коридор
    (410, 594, 500, 606, "entrance", "вход", False), # входная дверь
    (355,  12, 535,  26, "window",   "",    False),  # окно комнаты 10,5
    (610,  12, 775,  26, "window",   "",    False),  # окно кухни
    ( 30, 148, 140, 209, "window",   "",    False),  # окно комнаты 17,1
]

def poly(pts):
    return "M " + " L ".join("%g %g" % p for p in pts) + " Z"

def rect(x0, y0, x1, y1, **kw):
    at = " ".join('%s="%s"' % (k.replace("_","-"), v) for k, v in kw.items())
    return '<rect x="%g" y="%g" width="%g" height="%g" %s/>' % (x0, y0, x1-x0, y1-y0, at)

def build():
    o = []; a = o.append
    a('<svg viewBox="-34 -34 890 856" role="img" aria-label="План квартиры 43,6 квадратных метра: '
      'две изолированные комнаты 17,1 и 10,5, кухня 6,9, прихожая 3,4, коридор, раздельный санузел '
      '— туалет 0,9 и ванная 2,3 — и балкон. Показаны дверные проёмы и окна">')
    a('<g font-family="Golos Text, system-ui, sans-serif">')

    a('<!-- массив стен -->')
    a('<path fill="var(--line-strong)" fill-rule="evenodd" d="%s %s"/>'
      % (poly(SHELL), " ".join(poly(p) for _,_,_,p,_ in ROOMS)))

    a('<!-- балкон -->')
    a('<path fill="var(--surface-2)" stroke="var(--line-strong)" stroke-width="8" d="%s"/>' % poly(BALCONY))

    a('<!-- помещения -->')
    for rid, _, _, pts, _ in ROOMS:
        a('<path id="rm-%s" fill="var(--surface)" d="%s"/>' % (rid, poly(pts)))

    a('<!-- проёмы -->')
    for x0, y0, x1, y1, kind, label, exact in OPENINGS:
        if kind == "window":
            a(rect(x0, y0, x1, y1, fill="var(--surface-2)"))
            if x1-x0 > y1-y0:
                yc = (y0+y1)/2
                a('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="var(--ink-3)" stroke-width="3"/>' % (x0, yc, x1, yc))
            else:
                xc = (x0+x1)/2
                a('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="var(--ink-3)" stroke-width="3"/>' % (xc, y0, xc, y1))
        elif kind == "entrance":
            a(rect(x0, y0, x1, y1, fill="var(--accent-wash)", stroke="var(--accent)", stroke_width="3"))
        else:
            a(rect(x0, y0, x1, y1, fill="var(--surface)"))

    a('<!-- подписи помещений -->')
    for rid, name, area, pts, (lx, ly) in ROOMS:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        w = max(xs)-min(xs); h = max(ys)-min(ys)
        a('<text x="%g" y="%g" text-anchor="middle" font-size="21" font-weight="600" fill="var(--ink)">%s</text>' % (lx, ly, name))
        a('<text x="%g" y="%g" text-anchor="middle" font-size="18" fill="var(--ink-2)">%s м²</text>' % (lx, ly+23, area))
        a('<text x="%g" y="%g" text-anchor="middle" font-size="14" fill="var(--ink-3)" '
          'font-family="JetBrains Mono, monospace">%d × %d</text>' % (lx, ly+44, w, h))

    bx = 131; by = 74
    a('<text x="%g" y="%g" text-anchor="middle" font-size="19" font-weight="600" fill="var(--ink-2)">Балкон</text>' % (bx, by))
    a('<text x="%g" y="%g" text-anchor="middle" font-size="14" fill="var(--ink-3)" '
      'font-family="JetBrains Mono, monospace">263 × 148</text>' % (bx, by+22))

    a('<!-- ширины проёмов -->')
    for x0, y0, x1, y1, kind, label, exact in OPENINGS:
        if not label: continue
        cx, cy = (x0+x1)/2, (y0+y1)/2
        fill = "var(--accent-ink)" if kind == "entrance" else "var(--ink-3)"
        rot = "" if (x1-x0) >= (y1-y0) else ' transform="rotate(-90 %g %g)"' % (cx, cy)
        a('<text x="%g" y="%g" text-anchor="middle" font-size="13" font-weight="600" fill="%s" '
          'font-family="JetBrains Mono, monospace"%s>%s</text>' % (cx, cy+5, fill, rot, label))

    a('</g></svg>')
    return "\n".join(o)

PREVIEW = '''<!doctype html><meta charset=utf-8><title>План квартиры</title>
<style>
:root{--bg:#E6E6E2;--surface:#F7F7F4;--surface-2:#EFEFEB;--ink:#16181A;--ink-2:#4E5358;--ink-3:#7C8288;--line:#CBCBC4;--line-strong:#A9A99F;--accent:#9A6A05;--accent-ink:#6E4C03;--accent-wash:#F0E3C6}
@media(prefers-color-scheme:dark){:root{--bg:#121415;--surface:#1A1D1F;--surface-2:#212527;--ink:#E9E9E4;--ink-2:#A6ACB1;--ink-3:#7B8288;--line:#2C3134;--line-strong:#454B4F;--accent:#E2AC46;--accent-ink:#F0C377;--accent-wash:#33280F}}
body{background:var(--bg);color:var(--ink);font:16px/1.55 "Golos Text",system-ui,sans-serif;margin:0;padding:24px}
h1{font-size:21px;margin:0 0 6px}p{color:var(--ink-2);font-size:14px;margin:0 0 18px;max-width:74ch}
.wrap{background:var(--surface);border:1px solid var(--line-strong);padding:20px;max-width:960px}
svg{width:100%;height:auto;display:block}
</style>
<h1>План квартиры</h1>
<p>Размеры в сантиметрах. Помещения и дверные проёмы сняты с плана точно; окна и входная дверь
восстановлены по логике и требуют замера на объекте.</p>
<div class="wrap">__SVG__</div>'''

if __name__ == "__main__":
    svg = build()
    if "--preview" in sys.argv:
        open(__file__.rsplit("/",1)[0] + "/plan-preview.html", "w").write(PREVIEW.replace("__SVG__", svg))
        print("превью записано, SVG %d байт" % len(svg))
    else:
        sys.stdout.write(svg)
