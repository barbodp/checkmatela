"""Builds the homepage hero showcase (the rotating product carousel) and injects it into index.html
between the <!-- SHOWCASE:START --> and <!-- SHOWCASE:END --> markers.

Adding products later:
  * King (men):   add the product card to king.html + drop its photo in assets/img/products/, run
                  tools/make_king_cutouts.py, then re-run this script  -> a new slide appears automatically.
  * Pawn (kids):  new colourways show up automatically once assets/img/pawn/<line>/<colour>/hero.webp exists
                  (tools/make_hero_cutouts.py) and the colour is listed in tools/gen_pawn_pages.py.
  * Bishop / Rook: add an entry to OBJECTS below (they use studio cutouts, not model photos).
  * Any other category (e.g. Queen once it has photography): add a builder like king_slides() and list it in main().

Run from anywhere:  python3 tools/gen_home_showcase.py
"""
import os, re, json, html
from PIL import Image
import numpy as np
from gen_pawn_pages import LINES as PAWN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
esc = html.escape

CATS = {  # key -> (chip label, department, glyph id, page)
    "king": ("King", "Men", "glyph-king", "king.html"),
    "pawn": ("Pawn", "Kids", "glyph-pawn", "pawn.html"),
    "bishop": ("Bishop", "Accessories", "glyph-bishop", "bishop.html"),
    "rook": ("Rook", "Shoes", "glyph-rook", "rook.html"),
}
CHIP_ORDER = ["king", "pawn", "bishop", "rook"]

# Studio-cutout products (accessories & shoes): name, tag, price, image, width-% in the stage, alt
OBJECTS = {
    "bishop": [
        dict(name="The En Passant", tag="Silk Bow Tie", price=85, img="assets/img/hero/cat-bowtie.webp", w=58, alt="Black silk bow tie"),
        dict(name="The Fianchetto", tag="Silk Pocket Square", price=65, img="assets/img/hero/cat-pocketsquare.webp", w=54, alt="White silk pocket square"),
        dict(name="The Zugzwang", tag="Brass Knot Cufflinks", price=120, img="assets/img/hero/cat-cufflinks.webp", w=54, alt="Brass knot cufflinks"),
    ],
    "rook": [
        dict(name="The Back Rank", tag="Black Calfskin Oxford", price=310, img="assets/img/hero/cat-shoes.webp", w=76, alt="Black calfskin oxford shoes"),
    ],
}

# King cutouts are picked up from king.html; the welcome slide lineup is (king product image basename | pawn line/colour)
WELCOME = [("king", "caro-kann-navy-plaid"), ("pawn", "slim-fit/navy"), ("king", "queens-gambit-graphite"), ("pawn", "tuxedo/burgundy")]


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def king_products():
    src = read("king.html")
    out = []
    for blk in re.findall(r'<a class="product-card".*?</a>', src, re.S):
        img = re.search(r'<img src="assets/img/products/([^"]+)\.jpg"', blk)
        name = re.search(r"<h4>(.*?)</h4>", blk)
        tag = re.search(r'class="piece-tag">(.*?)</span>', blk)
        price = re.search(r'product-card__price">\$([\d,]+)', blk)
        note = re.search(r'product-card__notation">(.*?)</span>', blk)
        alt = re.search(r'alt="([^"]*)"', blk)
        if not (img and name and tag and price):
            continue
        slug = img.group(1)
        if not os.path.exists(os.path.join(ROOT, "assets/img/king", slug + ".webp")):
            print("  ! no cutout for", slug, "- run tools/make_king_cutouts.py; skipped")
            continue
        out.append(dict(slug=slug, name=name.group(1), tag=tag.group(1), price=price.group(1),
                        note=note.group(1) if note else "", alt=alt.group(1) if alt else name.group(1)))
    return out


def swatch_hex(path):
    """Dominant garment colour of a cutout (ignores near-white shirt/skin) for the colour dots."""
    im = np.asarray(Image.open(path).convert("RGBA"))
    h, w, _ = im.shape
    reg = im[int(h * .28):int(h * .68), int(w * .28):int(w * .72)].reshape(-1, 4)
    reg = reg[reg[:, 3] > 200][:, :3].astype(int)
    reg = reg[reg.min(axis=1) < 205]
    if len(reg) == 0:
        return "#cccccc"
    q = reg // 32
    keys = q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2]
    mode = np.bincount(keys).argmax()
    m = reg[keys == mode].mean(axis=0).astype(int)
    return "#%02x%02x%02x" % tuple(m)


def rel(p):
    return p.replace("\\", "/")


def glyph(gid, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 100 100" aria-hidden="true"><use href="#{gid}" fill="currentColor"/></svg>'


ARROW = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>'


def fig(src, x, h=None, w=None, z=1, op=1, alt="", focal=False, d=0, extra="", b=0):
    style = f"--x:{x}%;--z:{z};--op:{op};--d:{d}ms;--b:{b}%;" + (f"--h:{h}%;" if h else "") + (f"--w:{w}%;" if w else "")
    cls = "sc-fig" + (" is-focal" if focal else "") + (" is-obj" if w else "")
    return f'<div class="{cls}" style="{style}"{extra}><img data-src="{src}" alt="{esc(alt)}" draggable="false"></div>'


def copy_block(cat, title, sub, meta, cta_href, cta_label, extra="", h="h2"):
    label, dept, gid, _ = CATS[cat]
    n = CHIP_ORDER.index(cat) + 1
    sub_html = f'\n        <p class="sc-sub">{sub}</p>' if sub else ""
    return f'''<div class="sc-copy" data-cat="{cat}">
        <span class="sc-eyebrow">{glyph(gid)}<u>Chapter {n:02d}: <em>{label}</em> — {dept}</u></span>
        <{h} class="sc-title">{title}</{h}>{sub_html}
        <p class="sc-meta">{meta}</p>{extra}
        <div class="sc-cta"><a href="{cta_href}" class="btn">{cta_label}</a></div>
      </div>'''


def named(name, tag, connector="in"):
    """Editorial two-line title: 'The Sicilian' / indented '*in* Onyx Tuxedo'."""
    return f'{name}<span class="sc-line"><em>{connector}</em> {tag}</span>'


def king_slides():
    prods = king_products()
    slides = []
    n = len(prods)
    for i, p in enumerate(prods):
        L, R = prods[(i - 1) % n], prods[(i + 1) % n]
        src = lambda q: f"assets/img/king/{q['slug']}.webp"
        figs = (fig(src(L), 20, h=84, z=1, op=.9, d=160) + fig(src(R), 80, h=84, z=1, op=.9, d=160) +
                fig(src(p), 50, h=97, z=2, alt=f"{p['name']} — {p['tag']}", focal=True))
        meta = f"[ ${p['price']} ]" + (f'<i></i>Opening {esc(p["note"])}' if p["note"] else "")
        slides.append(dict(cat="king", figs=figs,
                           copy=copy_block("king", named(p["name"], p["tag"]), "", meta, "king.html", "Shop King")))
    return slides


def pawn_slides():
    slides = []
    for key in ["slim-fit", "suit-vest-set", "tuxedo", "tuxedo-vest-set"]:
        cfg = PAWN[key]
        cols = [(s, n) for s, n in cfg["colors"] if os.path.exists(os.path.join(ROOT, f"assets/img/pawn/{key}/{s}/hero.webp"))]
        if not cols:
            continue
        data = [dict(s=s, n=html.unescape(n), h=swatch_hex(os.path.join(ROOT, f"assets/img/pawn/{key}/{s}/hero.webp"))) for s, n in cols]
        start = next((i for i, (s, _) in enumerate(cols) if s == cfg["hero"][0]), 0)
        m = len(cols)
        base = f"assets/img/pawn/{key}"
        pick = lambda o: f"{base}/{cols[(start + o) % m][0]}/hero.webp"
        figs = (fig(pick(-1), 22, h=76, z=1, op=.92, d=160, extra=' data-slot="-1"') +
                fig(pick(1), 78, h=76, z=1, op=.92, d=160, extra=' data-slot="1"') +
                fig(pick(0), 50, h=88, z=2, alt=f"Boy's {cfg['label']} suit in {html.unescape(cols[start][1])}", focal=True, extra=' data-slot="0"'))
        dots = "".join(f'<button type="button" class="sc-dot{" is-on" if i == start else ""}" style="--c:{c["h"]}" data-i="{i}" aria-label="{esc(c["n"])}"></button>' for i, c in enumerate(data))
        extra = f'\n        <div class="sc-colors"><span class="sc-colorname">{esc(data[start]["n"])}</span><span class="sc-dots">{dots}</span></div>'
        intro = re.split(r"(?<=[.!?—])\s", cfg["intro"])[0].rstrip("—").strip()
        meta = f"[ From ${cfg['price']} ]<i></i>{m} colourways"
        c = copy_block("pawn", named(cfg["label"], f"{m} colours"), esc(intro), meta, cfg["file"], f"Shop {cfg['label']}", extra)
        slides.append(dict(cat="pawn", figs=figs, copy=c, attrs=f"data-colors='{json.dumps(data)}' data-base=\"{base}\" data-start=\"{start}\""))
    return slides


def object_slides(cat):
    items = OBJECTS[cat]
    slides = []
    for i, p in enumerate(items):
        others = [q for j, q in enumerate(items) if j != i]
        figs = ""
        if others:
            pos = [(20, 10), (80, 10)] if len(others) > 1 else [(82, 6)]
            for q, (x, b) in zip(others, pos):
                figs += fig(q["img"], x, w=q["w"] * .5, z=1, op=.92, d=160, b=b)
        figs += fig(p["img"], 50, w=p["w"], z=2, alt=p["alt"], focal=True, b=24 if len(items) > 1 else 14)
        slides.append(dict(cat=cat, figs=figs, copy=copy_block(cat, named(p["name"], p["tag"]), "", f"[ ${p['price']} ]", CATS[cat][3], f"Shop {CATS[cat][0]}")))
    return slides


def welcome_slide():
    figs = ""
    xs = [15, 38, 62, 85]
    for (kind, ref), x in zip(WELCOME, xs):
        if kind == "king":
            figs += fig(f"assets/img/king/{ref}.webp", x, h=94, z=2, op=1, d=(x // 4) * 6, alt="")
        else:
            figs += fig(f"assets/img/pawn/{ref}/hero.webp", x, h=72, z=2, op=1, d=(x // 4) * 6, alt="")
    copy = f'''<div class="sc-copy sc-copy--welcome" data-cat="welcome">
        <span class="sc-eyebrow">{glyph("glyph-king")}<u>Checkmatela — <em>Formal</em> wear<span class="sc-hide-sm">&nbsp;<em>for</em> every piece</span></u></span>
        <h1 class="sc-title">Every move,<br><em>tailored.</em></h1>
        <p class="sc-sub">Suits, tuxedos, accessories and shoes cut with a grandmaster's precision — for men, boys and every moment that decides everything.</p>
        <div class="sc-cta"><a href="king.html" class="btn">Shop the collection</a><a href="#diagram" class="btn">Explore the set</a></div>
      </div>'''
    return dict(cat="welcome", figs=figs, copy=copy)


def interleave(groups):
    """Spread the categories evenly through the sequence (King 10, Pawn 4, ... -> K P K B K R ...)."""
    keyed = []
    for gi, g in enumerate(groups):
        for i, s in enumerate(g):
            keyed.append(((i + .5) / len(g), gi, s))
    return [s for _, _, s in sorted(keyed, key=lambda t: (t[0], t[1]))]


def build():
    seq = [welcome_slide()] + interleave([king_slides(), pawn_slides(), object_slides("bishop"), object_slides("rook")])
    copies, stages = [], []
    for i, s in enumerate(seq):
        glyph_id = CATS[s["cat"]][2] if s["cat"] in CATS else "glyph-king"
        cls = "sc-figs" + (" sc-figs--obj" if s["cat"] in ("bishop", "rook") else "")
        stages.append(f'''<div class="{cls}" data-cat="{s["cat"]}" data-i="{i}" {s.get("attrs", "")}>
        <span class="sc-glyph">{glyph(glyph_id)}</span>
        {s["figs"]}
      </div>''')
        copies.append(s["copy"].replace('class="sc-copy', f'data-i="{i}" class="sc-copy' + (" is-active" if i == 0 else ""), 1))
    # first slide: real src (+ high priority) so the hero paints straight away; the rest lazy-load from showcase.js
    stages[0] = stages[0].replace('<img data-src="', '<img fetchpriority="high" src="')
    chips = "".join(f'''<button type="button" class="sc-chip" data-cat="{k}"><span class="sc-chip__n">{CHIP_ORDER.index(k) + 1:02d}</span><span>{CATS[k][0]}</span></button>'''
                    for k in CHIP_ORDER)
    return f'''<section class="showcase" id="showcase" aria-roledescription="carousel" aria-label="Featured Checkmatela collection" data-count="{len(seq)}">
  <div class="showcase__bg"></div>
  <div class="showcase__inner">
    <div class="sc-copies" aria-live="off">
      {chr(10).join("      " + c for c in copies).strip()}
    </div>
    <div class="sc-stage">
      {chr(10).join("      " + s for s in stages).strip()}
      <div class="sc-wipe" aria-hidden="true"></div>
    </div>
  </div>
  <div class="showcase__bar">
    <i class="sc-progress"></i>
    <div class="showcase__bar-inner">
      <div class="sc-chips" role="group" aria-label="Jump to a collection">{chips}</div>
      <div class="sc-nav">
        <button type="button" class="sc-arrow" data-dir="-1" aria-label="Previous"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M19 12H5M11 5l-7 7 7 7"/></svg></button>
        <span class="sc-count">[ <b>01</b> / {len(seq):02d} ]</span>
        <button type="button" class="sc-arrow" data-dir="1" aria-label="Next"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14M13 5l7 7-7 7"/></svg></button>
      </div>
    </div>
  </div>
</section>'''


def main():
    block = build()
    src = read("index.html")
    a, b = "<!-- SHOWCASE:START -->", "<!-- SHOWCASE:END -->"
    i, j = src.index(a) + len(a), src.index(b)
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(src[:i] + "\n" + block + "\n" + src[j:])
    print("showcase:", re.search(r'data-count="(\d+)"', block).group(1), "slides")


if __name__ == "__main__":
    main()
