"""Three professional logo directions for Orion Syndic (text outlined from local fonts)."""
import json, math, sys, pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

TG = "/usr/share/texmf/fonts/opentype/public/tex-gyre/"
GF = "/usr/share/fonts/truetype/google-fonts/"
ADV_B, ADV_R = TG + "texgyreadventor-bold.otf", TG + "texgyreadventor-regular.otf"
POP_B, POP_R = GF + "Poppins-Bold.ttf", GF + "Poppins-Regular.ttf"
NAVY, GOLD, WHITE = "#0F2340", "#E3A21A", "#FFFFFF"
_cache = {}

def font(path):
    if path not in _cache:
        f = TTFont(path); _cache[path] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _cache[path]

def ntos(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

def run(path, text, size, x, base, track=0.0):
    """Outline a text run; returns (svg path d, advance width)."""
    f, gs, cmap, upm = font(path); s = size / upm
    pen = SVGPathPen(gs, ntos=ntos); cx = x
    for i, ch in enumerate(text):
        g = gs[cmap[ord(ch)]]
        g.draw(TransformPen(pen, (s, 0, 0, -s, cx, base)))
        cx += g.width * s + (track if i < len(text) - 1 else 0)
    return pen.getCommands(), cx - x

def size_for_x(path, xh):
    f, gs, cmap, upm = font(path)
    return xh * upm / f["OS/2"].sxHeight

def size_for_cap(path, cap):
    f, gs, cmap, upm = font(path)
    return cap * upm / f["OS/2"].sCapHeight

def sparkle(cx, cy, rv, rh, k=1.1):
    return (f"M{ntos(cx)} {ntos(cy-rv)}Q{ntos(cx+k)} {ntos(cy-k)} {ntos(cx+rh)} {ntos(cy)}"
            f"Q{ntos(cx+k)} {ntos(cy+k)} {ntos(cx)} {ntos(cy+rv)}Q{ntos(cx-k)} {ntos(cy+k)} {ntos(cx-rh)} {ntos(cy)}"
            f"Q{ntos(cx-k)} {ntos(cy-k)} {ntos(cx)} {ntos(cy-rv)}Z")

def arc_pt(cx, cy, r, deg):
    a = math.radians(deg); return cx + r * math.cos(a), cy + r * math.sin(a)

# ---------- A : Étoile (an O with a star in its opening) ----------
def mark_A(ring, star, cx=30, cy=34, r=21, sw=7.4, gap_at=-50, gap=34, s=1.0, ox=0, oy=0):
    T = lambda v: v * s
    x1, y1 = arc_pt(cx, cy, r, gap_at + gap); x2, y2 = arc_pt(cx, cy, r, gap_at - gap + 360)
    sx, sy = arc_pt(cx, cy, r, gap_at)
    g = (f'<g transform="translate({ntos(ox)} {ntos(oy)}) scale({ntos(s)})">'
         f'<path d="M{ntos(x1)} {ntos(y1)}A{r} {r} 0 1 1 {ntos(x2)} {ntos(y2)}" fill="none" stroke="{ring}" stroke-width="{sw}" stroke-linecap="round"/>'
         f'<path d="{sparkle(sx, sy, 11, 9)}" fill="{star}"/></g>')
    return g

def word_A(color, x=66):
    xs = size_for_x(ADV_B, 23)
    d1, w1 = run(ADV_B, "orion", xs, x, 45.5, 0.2)
    d2, w2 = run(ADV_R, "syndic", xs, x + w1 + xs * 0.28, 45.5, 0.2)
    return f'<path d="{d1}" fill="{color}"/><path d="{d2}" fill="{color}"/>', x + w1 + xs * 0.28 + w2

# ---------- B : Constellation (Orion drawn in a tile) ----------
B_STARS = [(18, 14, 3.4, "g"), (46, 16, 2.5, "w"), (26, 33, 2.3, "w"), (32, 31, 2.3, "w"), (38, 29, 2.3, "w"), (20, 50, 2.5, "w"), (45, 49, 3.0, "w")]
B_LINES = [(0, 2), (1, 4), (2, 3), (3, 4), (2, 5), (4, 6)]
def mark_B(tile, star, accent, line_op=.45):
    lines = "".join(f'<line x1="{B_STARS[a][0]}" y1="{B_STARS[a][1]}" x2="{B_STARS[b][0]}" y2="{B_STARS[b][1]}" stroke="{star}" stroke-opacity="{line_op}" stroke-width="1.5" stroke-linecap="round"/>' for a, b in B_LINES)
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{accent if c == "g" else star}"/>' for x, y, r, c in B_STARS)
    return f'<rect width="64" height="64" rx="15" fill="{tile}"/>{lines}{dots}'

def word_B(color, sub, x=80):
    cs = size_for_cap(ADV_B, 22)
    d1, w1 = run(ADV_B, "ORION", cs, x, 43, cs * 0.06)
    d2, w2 = run(ADV_R, "SYNDIC", cs, x + w1 + cs * 0.32, 43, cs * 0.06)
    return f'<path d="{d1}" fill="{color}"/><path d="{d2}" fill="{sub}"/>', x + w1 + cs * 0.32 + w2

# ---------- C : Toit (an O with a gable, star inside) ----------
def mark_C(line, star):
    return (f'<path d="M11 32 32 13.5 53 32V38.5A21 21 0 0 1 11 38.5Z" fill="none" stroke="{line}" stroke-width="6.6" stroke-linejoin="round"/>'
            f'<path d="{sparkle(32, 38, 8, 6.5, .9)}" fill="{star}"/>')

def word_C(color, x=68):
    cs = size_for_cap(POP_B, 23)
    d1, w1 = run(POP_B, "Orion", cs, x, 45, 0)
    d2, w2 = run(POP_R, "Syndic", cs, x + w1 + cs * 0.24, 45, 0)
    return f'<path d="{d1}" fill="{color}"/><path d="{d2}" fill="{color}"/>', x + w1 + cs * 0.24 + w2

def svg(inner, w, h=64, px=None):
    px = px or w * 8
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ntos(w)} {h}" width="{ntos(px)}" height="{ntos(px * h / w)}">{inner}</svg>'

def build():
    out = {}
    wa, ea = word_A(NAVY); wa_w, _ = word_A(WHITE)
    out["A"] = {
        "name": "Étoile",
        "light": svg(mark_A(NAVY, GOLD) + wa, ea + 2),
        "dark": svg(mark_A(WHITE, GOLD) + wa_w, ea + 2),
        "icon": svg(f'<rect width="64" height="64" rx="15" fill="{NAVY}"/>' + mark_A(WHITE, GOLD, s=.78, ox=7.5, oy=5.2), 64, px=512),
    }
    wb, eb = word_B(NAVY, NAVY); wb_w, _ = word_B(WHITE, WHITE)
    out["B"] = {
        "name": "Constellation",
        "light": svg(mark_B(NAVY, WHITE, GOLD) + wb, eb + 2),
        "dark": svg(mark_B(WHITE, NAVY, GOLD, .35) + wb_w, eb + 2),
        "icon": svg(mark_B(NAVY, WHITE, GOLD), 64, px=512),
    }
    wc, ec = word_C(NAVY); wc_w, _ = word_C(WHITE)
    out["C"] = {
        "name": "Toit",
        "light": svg(mark_C(NAVY, GOLD) + wc, ec + 2),
        "dark": svg(mark_C(WHITE, GOLD) + wc_w, ec + 2),
        "icon": svg(f'<rect width="64" height="64" rx="15" fill="{NAVY}"/><g transform="translate(6.4 5.6) scale(.8)">' + mark_C(WHITE, GOLD) + "</g>", 64, px=512),
    }
    # adaptive inline version of A for the website (follows light/dark tokens)
    wi, ei = word_A("var(--ink)")
    inline = (f'<svg class="logo" viewBox="0 0 {ntos(ei + 2)} 64" role="img" aria-label="Orion Syndic">'
              + mark_A("var(--ink)", "var(--star)").replace('stroke="var(--ink)"', 'style="stroke:var(--ink)"').replace('fill="var(--star)"', 'style="fill:var(--star)"')
              + wi.replace('fill="var(--ink)"', 'style="fill:var(--ink)"') + "</svg>")
    icon_inline = svg(f'<rect width="64" height="64" rx="15" fill="{NAVY}"/>' + mark_A(WHITE, GOLD, s=.78, ox=7.5, oy=5.2), 64, px=64)
    return out, inline, icon_inline

if __name__ == "__main__":
    dst = pathlib.Path(sys.argv[1]); dst.mkdir(parents=True, exist_ok=True)
    opts, inline, icon_inline = build()
    for k, o in opts.items():
        for variant in ("light", "dark", "icon"):
            (dst / f"logo-{k}-{variant}.svg").write_text(o[variant])
    (dst / "logo2_inline.json").write_text(json.dumps({"inline": inline, "favicon": icon_inline, "options": {k: o["name"] for k, o in opts.items()}}))
    print("ok", {k: o["name"] for k, o in opts.items()})
