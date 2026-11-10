"""Primary logo without any AI-style sparkle: the 'quote-part' house + Helvetica-style wordmark."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_logo2 import run, size_for_x, svg, ntos, TG

HER_B, HER_R = TG + "texgyreheros-bold.otf", TG + "texgyreheros-regular.otf"
INK, BLUE, WHITE, BLUE_LIGHT = "#0B1220", "#1D3FE0", "#FFFFFF", "#8EA4FF"

def mark(left, right):
    return (f'<path d="M8 30 32 9 37 13.4V55H8Z" fill="{left}" stroke="{left}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M41 16.9 56 30V55H41Z" fill="{right}" stroke="{right}" stroke-width="3" stroke-linejoin="round"/>')

def word(color, x=74):
    xs = size_for_x(HER_B, 25)
    d1, w1 = run(HER_B, "orion", xs, x, 47, -0.35)
    g = xs * .26
    d2, w2 = run(HER_R, "syndic", xs, x + w1 + g, 47, -0.35)
    return d1, d2, x + w1 + g + w2

d1, d2, end = word("#000")
W = round(end + 2, 2)
files = {
    "light": svg(mark(INK, BLUE) + f'<path d="{d1}" fill="{INK}"/><path d="{d2}" fill="{INK}"/>', W),
    "dark": svg(mark(WHITE, BLUE_LIGHT) + f'<path d="{d1}" fill="{WHITE}"/><path d="{d2}" fill="{WHITE}"/>', W),
    "icon": svg(f'<rect width="64" height="64" rx="14" fill="{BLUE}"/><g transform="translate(8.3 8.6) scale(.74)">' + mark(WHITE, BLUE_LIGHT) + "</g>", 64, px=512),
}
inline = (f'<svg class="logo" viewBox="0 0 {ntos(W)} 64" role="img" aria-label="Orion Syndic">'
          '<path d="M8 30 32 9 37 13.4V55H8Z" style="fill:var(--logo-ink);stroke:var(--logo-ink)" stroke-width="3" stroke-linejoin="round"/>'
          '<path d="M41 16.9 56 30V55H41Z" style="fill:var(--logo-accent);stroke:var(--logo-accent)" stroke-width="3" stroke-linejoin="round"/>'
          f'<path d="{d1}" style="fill:var(--logo-ink)"/><path d="{d2}" style="fill:var(--logo-ink)"/></svg>')
favicon = svg(f'<rect width="64" height="64" rx="14" fill="{BLUE}"/><g transform="translate(8.3 8.6) scale(.74)">' + mark(WHITE, BLUE_LIGHT) + "</g>", 64, px=64)

if __name__ == "__main__":
    d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True, exist_ok=True)
    for k, s in files.items():
        (d / f"logo-orion-syndic-{k}.svg").write_text(s)
    (d / "logo4_inline.json").write_text(json.dumps({"inline": inline, "favicon": favicon}))
    print("ok", W)
