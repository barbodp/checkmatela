"""Builds the Antonio Uomo section under Men (King) from tools/catalog/antonio-uomo.json (made by tools/au_fetch.py).

  antonio-uomo.html                         the brand page: one card per product type
  antonio-uomo-<type>.html                  a product-type page (e.g. 2 Piece Slim Fit Single Breasted Suits): every colour, with a colour filter
  antonio-uomo-<style>-<colour>-<code>.html  one page per colour ("Indigo 2 Piece Slim Fit Single Breasted Suit"): photos, price, size picker, details and a pop-up size chart (the chart the supplier shows for that product)

It also refreshes the "Shop by brand" banner on king.html (between BRANDS markers). Run:  python3 tools/gen_antonio.py   (gen_nav.py runs at the end).
"""
import os, json, re, html
from gen_pawn_pages import HEADER, FOOTER, ANNOUNCE, CSS_VERSION, FAVICON
from gen_info_pages import glyph_defs
from shoplib import shop_block, replace_between, esc
import au_sizes
import suit_info
from suit_info import DESIGN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = json.load(open(os.path.join(ROOT, "tools", "catalog", "antonio-uomo.json"), encoding="utf-8"))
BRAND = "Antonio Uomo"
BRAND_FILE = "antonio-uomo.html"
ASSET = "assets/img/antonio-uomo/"

TYPE_ORDER = ["2-piece-slim-fit-single-breasted-suits", "3-piece-slim-fit-suits", "3-piece-classic-fit-suits", "3-piece-textured-suits", "3-piece-plaid-suits",
              "2-piece-slim-fit-tuxedos", "3-piece-slim-fit-tuxedos", "3-piece-slim-fit-double-breasted-tuxedos", "slim-fit-dress-pants", "patterned-jackets"]
BLURB = {
    "2-piece-slim-fit-single-breasted-suits": "Jacket and trousers in a modern slim cut, for weddings, school events and work.",
    "3-piece-slim-fit-suits": "Jacket, vest and trousers in a slim, contemporary cut.",
    "3-piece-classic-fit-suits": "Jacket, vest and trousers in a roomier classic cut, with sizes up to 62.",
    "3-piece-textured-suits": "Slim-fit three-piece suits in textured and shiny fabrics.",
    "3-piece-plaid-suits": "Slim-fit three-piece suits in plaid.",
    "2-piece-slim-fit-tuxedos": "Slim-fit tuxedo jacket and trousers for black tie, prom and weddings.",
    "3-piece-slim-fit-tuxedos": "Slim-fit tuxedo with jacket, vest and trousers for black tie, prom and weddings.",
    "3-piece-slim-fit-double-breasted-tuxedos": "A double-breasted take on the slim-fit three-piece tuxedo.",
    "slim-fit-dress-pants": "Stretch dress pants with a flat front and a slim, straight leg.",
    "patterned-jackets": "Shiny patterned jackets, a standout piece for any formal occasion.",
}
FAMILY_ORDER = ["Black", "Charcoal", "Grey", "Silver", "Navy", "Blue", "Teal", "Green", "Burgundy", "Red", "Pink", "Purple", "Brown", "Beige", "Gold", "White", "Other"]
CRUMB = '<div class="crumbs">{}</div>'


def money(n):
    return f"${n:g}"


def img(key, kind=""):
    return f"{ASSET}{key}{kind}.webp"


def img_url(im, kind=""):
    """Antonio photos are addressed by md5 key (three sizes); King photos by a plain path."""
    return im["path"] if "path" in im else img(im["key"], kind)


def pieces(it):
    if it.get("pieces"):
        return it["pieces"]
    m = re.match(r"(\d) Piece", it["style"])
    return int(m.group(1)) if m else 0


def sorted_items(items):
    return sorted(items, key=lambda i: (FAMILY_ORDER.index(i["family"]) if i["family"] in FAMILY_ORDER else 99, i["colour"], i["code"]))


TYPES = {}
for _it in ITEMS:
    TYPES.setdefault(_it["type_slug"], []).append(_it)
ORDERED = [s for s in TYPE_ORDER if s in TYPES] + [s for s in TYPES if s not in TYPE_ORDER]


def tfile(slug):
    return f"antonio-uomo-{slug}.html"


def pfile(it):
    return it.get("file") or f"antonio-uomo-{it['slug']}.html"


def crumbs(*parts):
    out, last = [], parts[-1]
    for label, href in parts[:-1]:
        out.append(f'<a href="{href}">{esc(label)}</a>')
    out.append(f"<span>{esc(last[0])}</span>")
    return CRUMB.format(' <span>/</span> '.join(out))


BASE_CRUMBS = [("Home", "index.html"), ("Men", "king.html"), (BRAND, BRAND_FILE)]


def shell(title, meta, body, glyph="glyph-king", extra_js=""):
    defs = glyph_defs(sorted({glyph, "glyph-king"}))
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta)}">
{FAVICON}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css?v={CSS_VERSION}">
</head>
<body>

<svg width="0" height="0" style="position:absolute">
  <defs>
{defs}
  </defs>
</svg>

{ANNOUNCE}

{HEADER}

{body}

{FOOTER}
'''
    if extra_js:
        page = page.replace('<script src="js/main.js"></script>', '<script src="js/main.js"></script>\n' + extra_js)
    return page


def hero(crumb_html, h1, lead, glyph="glyph-king"):
    return f'''<section class="cat-hero">
  <div class="cat-hero__bg"></div>
  <div class="cat-hero__fade"></div>
  <div class="cat-hero__inner">
    <div class="cat-hero__copy">
      {crumb_html}
      <span class="cat-hero__glyph"><svg viewBox="0 0 100 100"><use href="#{glyph}" fill="currentColor"/></svg></span>
      <h1>{esc(h1)}</h1>
      <p>{esc(lead)}</p>
    </div>
    <div class="cat-hero__figures cat-hero__figures--glyph">
      <svg viewBox="0 0 100 130" aria-hidden="true"><use href="#{glyph}" fill="currentColor"/></svg>
    </div>
  </div>
</section>'''


def write(name, text):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(text)


def price_range(items):
    ps = [i["price"] for i in items]
    return min(ps), max(ps)


def card(it):
    pic = img_url(it["images"][0], "-c")
    return f'''            <a class="product-card au-card" href="{pfile(it)}" data-id="{it.get("id", "antonio-uomo/" + it["slug"])}" data-name="{esc(it["name"])}" data-tag="{esc(it["type"])}" data-price="{money(it["price"])[1:]}" data-img="{pic}" data-f-color="{it["family"]}">
              <span class="au-card__img"><img src="{pic}" alt="{esc(it["name"])}" loading="lazy" width="480" height="720"></span>
              <div class="product-card__meta"><div><h4>{esc(it.get("colour", it["name"]))}</h4><span class="piece-tag">{esc(it["style"])} &middot; {esc(it["code"])}</span></div><span class="product-card__price">{money(it["price"])}</span></div>
            </a>'''


def build_brand():
    total = len(ITEMS)
    lo, hi = price_range(ITEMS)
    tiles = []
    for s in ORDERED:
        its = TYPES[s]
        lo_t, hi_t = price_range(its)
        name = its[0]["type"]
        first = sorted_items(its)[0]
        tiles.append(f'''      <a class="au-type" href="{tfile(s)}">
        <span class="au-type__img"><img src="{img(first["images"][0]["key"], "-c")}" alt="{esc(first["name"])}" loading="lazy" width="480" height="720"></span>
        <b>{esc(name)}</b>
        <span>{esc(BLURB.get(s, ""))}</span>
        <em>{len(its)} color{"s" if len(its) != 1 else ""} &middot; {"from " + money(lo_t) if lo_t != hi_t else money(lo_t)}</em>
      </a>''')
    body = f'''{hero(crumbs(*BASE_CRUMBS), BRAND, f"Suits, tuxedos, dress pants and jackets: {total} styles in {len(ORDERED)} product types, from {money(lo)}.")}

<section class="section" style="padding-bottom:0">
  <div class="container">
    <div class="section-head" data-reveal>
      <span class="eyebrow">The Brand</span>
      <h2>Well-made men's suits for the moments that matter.</h2>
      <p>Antonio Uomo designs men's suits and formal wear with quality and service in mind. Choose a product type to see every color, then pick your size.</p>
    </div>
    <div class="au-types" data-reveal-group>
{chr(10).join(tiles)}
    </div>
  </div>
</section>'''
    write(BRAND_FILE, shell(f"{BRAND} — Men's Suits & Tuxedos | Checkmatela", f"Antonio Uomo men's suits, tuxedos, dress pants and jackets at Checkmatela: {total} styles from {money(lo)}.", body))


def build_type(slug):
    its = sorted_items(TYPES[slug])
    name = its[0]["type"]
    lo, hi = price_range(its)
    fams = sorted({i["family"] for i in its}, key=FAMILY_ORDER.index)
    lead = f"{len(its)} color{'s' if len(its) != 1 else ''}, {'from ' + money(lo) if lo != hi else money(lo)}. {BLURB.get(slug, '')}"
    facets = [{"key": "color", "label": "Colour", "swatch": True}]
    cards = "\n".join(card(i) for i in its)
    shop_html = shop_block(cards, facets, "au", count_noun="colors", review_facets=[])
    others = "\n      ".join(f'<a href="{tfile(s)}" class="btn ghost">{esc(TYPES[s][0]["type"])}</a>' for s in ORDERED if s != slug)
    body = f'''{hero(crumbs(*BASE_CRUMBS, (name, tfile(slug))), name, lead)}

{shop_html}

<section class="section" style="background:var(--pine-deep);color:var(--paper);text-align:center;padding:64px 0">
  <div class="container" data-reveal>
    <span class="eyebrow" style="margin:0 auto">More from {BRAND}</span>
    <h2 style="margin-top:.4em;font-size:clamp(1.8rem,3vw,2.6rem)">Explore the rest of the collection.</h2>
    <div style="display:flex;gap:12px 16px;justify-content:center;margin-top:1.8em;flex-wrap:wrap">
      {others}
      <a href="{BRAND_FILE}" class="btn ghost">All {BRAND}</a>
    </div>
  </div>
</section>'''
    write(tfile(slug), shell(f"{name} — {BRAND} | Checkmatela", f"{name} by {BRAND}: {len(its)} colors, {'from ' + money(lo) if lo != hi else money(lo)}. Browse colors and sizes at Checkmatela.", body,
                           extra_js='<script src="js/shop.js?v=4"></script>'))


def gallery(it):
    """Main photo + thumbnails. The frame takes the exact aspect ratio of the photo on show (set from data-w/data-h, updated by js/product.js),
    so the photo always fills it edge to edge and the frame's own colour never shows."""
    thumbs = []
    for n, im in enumerate(it["images"], 1):
        thumbs.append(f'<button type="button" class="pdp-thumb{" is-active" if n == 1 else ""}" data-src="{img_url(im)}" data-w="{im["w"]}" data-h="{im["h"]}" aria-label="Show photo {n} of {len(it["images"])}"><img src="{img_url(im, "-t")}" alt="" loading="lazy" width="72" height="72"></button>')
    first = it["images"][0]
    h = round(900 * first["h"] / first["w"])
    main = f'<img id="pdpMain" src="{img_url(first)}" alt="{esc(it["name"])}" width="900" height="{h}" fetchpriority="high">'
    strip = f'<div class="pdp-thumbs">{"".join(thumbs)}</div>' if len(thumbs) > 1 else ""
    return f'<div class="pdp-gallery"><div class="pdp-main" id="pdpFrame" style="--r:{first["w"] / first["h"]:.4f}">{main}</div>{strip}</div>'


def chips(key, label, values, default=None):
    btns = "".join(f'<button type="button" class="chip-btn" data-v="{esc(v)}" aria-pressed="{"true" if v == default else "false"}">{esc(v)}</button>' for v in values)
    return f'<fieldset class="pdp-opt" data-key="{key}"><legend>{label}</legend><div class="pdp-chips">{btns}</div></fieldset>'


def acc(title, inner, open_=False):
    return f'<details class="pdp-acc"{" open" if open_ else ""}><summary>{title}</summary><div class="pdp-acc__body">{inner}</div></details>'


def pdp_body(it, *, eyebrow, codeline, crumb_parts, tag, related_html):
    """The product detail page body, shared by the Antonio Uomo pages and the King suits."""
    name = it["name"]
    paras = it["paras"]
    lede = paras[0] if paras else ""
    more = "".join(f"<p>{esc(p)}</p>" for p in paras[1:])
    bullets = "".join(f"<li>{esc(b)}</li>" for b in it["bullets"])
    n = pieces(it)
    design = ""
    if n in DESIGN:
        d = DESIGN[n]
        design = f"<p>{esc(d[0])}</p>" + "".join(f"<h4>{esc(t)}</h4><p>{esc(x)}</p>" for t, x in d[1:])
    details = (f"<ul class=\"pdp-list\">{bullets}</ul>" if bullets else "") + more
    sizes = chips("size", "Size", it["sizes"], None) if it["sizes"] else ""
    length = chips("length", "Length", it["lengths"], "Regular" if "Regular" in it["lengths"] else None) if it["lengths"] else ""
    chart_id = it.get("chart", "")                       # the size chart that goes with this product (the supplier's own, for Antonio pieces)
    has_chart = chart_id in au_sizes.CHARTS
    if chart_id and not has_chart:
        print("WARNING: no size chart data for", chart_id, "(", it["code"], ")")
    chart_btn = ('<button type="button" class="pdp-chart-btn" data-open-chart aria-haspopup="dialog"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M3 15 15 3l6 6L9 21z"/><path d="M7 11l2 2M10 8l2 2M13 5l2 2M5 13l1 1"/></svg>Size chart</button>' if has_chart else "")
    chart_dialog = (f'<dialog class="shop-dialog au-chart" id="sizeChart" aria-labelledby="auChartTitle"><button type="button" class="shop-dialog__x" aria-label="Close size chart">×</button>'
                    f'<div class="au-chart__body">{au_sizes.chart_html(chart_id)}</div></dialog>' if has_chart else "")
    return f'''<main class="pdp" id="pdp" data-id="{it.get("id", "antonio-uomo/" + it["slug"])}" data-name="{esc(name)}" data-tag="{esc(tag)}" data-price="{money(it["price"])[1:]}" data-img="{img_url(it["images"][0], "-c")}">
  <div class="container">
    {crumbs(*crumb_parts).replace('class="crumbs"', 'class="crumbs crumbs--light"')}
    <div class="pdp__grid">
      {gallery(it)}
      <div class="pdp-info">
        <span class="eyebrow">{eyebrow}</span>
        <h1>{esc(name)}</h1>
        <p class="pdp-code">{codeline}</p>
        <p class="pdp-price">{money(it["price"])}</p>
        <p class="pdp-lede">{esc(lede)}</p>
        {sizes}
        {length}
        {chart_btn}
        <p class="pdp-msg" role="status"></p>
        <div class="pdp-cta"><button type="button" class="btn pdp-add">Add to preview bag</button><a class="btn dark-ghost" href="book-a-fitting.html?look={esc(name.replace(" ", "%20"))}">Ask about fit</a></div>
        <p class="pdp-assure"><a href="shipping-returns.html">Free exchanges and easy returns</a></p>
        <p class="pdp-fine">Preview only: prices and availability are not confirmed, and checkout is not connected.</p>
        <div class="pdp-accs">
          {acc("Details", details, True)}
          {acc("About this look", design) if design else ""}
        </div>
      </div>
    </div>
  </div>
  {chart_dialog}
</main>

{related_html}'''


def build_product(it):
    slug, tname = it["type_slug"], it["type"]
    related = [i for i in sorted_items(TYPES[slug]) if i is not it][:4]
    rel_html = ""
    if related:
        rel_html = f'''<section class="section pdp-related">
  <div class="container">
    <div class="section-head"><span class="eyebrow">More colors</span><h2>{esc(tname)}</h2></div>
    <div class="product-grid">
{chr(10).join(card(r) for r in related)}
    </div>
    <p style="text-align:center;margin-top:28px"><a class="btn dark-ghost" href="{tfile(slug)}">See all {len(TYPES[slug])} colors</a></p>
  </div>
</section>'''
    body = pdp_body(it, eyebrow=f"{BRAND} &middot; Men", codeline=f"Style {esc(it['code'])} &middot; {esc(tname)}", tag=f"{BRAND} · {it['style']}",
                    crumb_parts=[*BASE_CRUMBS, (tname, tfile(slug)), (it["name"], pfile(it))], related_html=rel_html)
    write(pfile(it), shell(f"{it['name']} ({it['code']}) — {BRAND} | Checkmatela",
                           f"{it['name']} by {BRAND}, style {it['code']}, {money(it['price'])}. " + (it["bullets"][0] + ". " if it["bullets"] else "") + "Sizes, details and size chart at Checkmatela.",
                           body, extra_js='<script src="js/product.js?v=5"></script>'))


def king_items():
    """The King catalog (tools/catalog/king.json) in the same shape as the Antonio items, with the shared suit information."""
    cat = json.load(open(os.path.join(ROOT, "tools", "catalog", "king.json"), encoding="utf-8"))["products"]
    return [dict(slug=p["slug"], id=f"king/{p['slug']}", file=f"king-{p['slug']}.html", name=p["name"], colour=p["name"], code=p["notation"], style=p["tag"],
                 type="Men's suits & tuxedos", family=p["color"], price=p["price"], pieces=suit_info.KING_PIECES.get(p["style"], 2),
                 paras=[suit_info.LEDE], bullets=suit_info.BULLETS, sizes=suit_info.SIZES, lengths=suit_info.LENGTHS, chart=suit_info.CHART_ID,
                 images=[dict(path=f"assets/img/products/{p['slug']}.jpg", w=900, h=1350)]) for p in cat]


def build_king_products():
    items = king_items()
    for it in items:
        others = [o for o in items if o is not it][:4]
        rel = f'''<section class="section pdp-related">
  <div class="container">
    <div class="section-head"><span class="eyebrow">More from King</span><h2>Suits &amp; tuxedos</h2></div>
    <div class="product-grid">
{chr(10).join(card(r) for r in others)}
    </div>
    <p style="text-align:center;margin-top:28px"><a class="btn dark-ghost" href="king.html">See all of King</a></p>
  </div>
</section>'''
        body = pdp_body(it, eyebrow="King &middot; Men", codeline=f"{esc(it['style'])} &middot; {esc(it['code'])}", tag=it["style"],
                        crumb_parts=[("Home", "index.html"), ("Men", "king.html"), (it["name"], pfile(it))], related_html=rel)
        write(pfile(it), shell(f"{it['name']} — {it['style']} | Checkmatela",
                               f"{it['name']}, {it['style']}, {money(it['price'])}. " + suit_info.BULLETS[0] + ". Sizes, details and size chart at Checkmatela.", body,
                               extra_js='<script src="js/product.js?v=5"></script>'))
    print("king product pages:", len(items))


def build_king_banner():
    lo, hi = price_range(ITEMS)
    firsts = [sorted_items(TYPES[s])[0] for s in ORDERED[:4]]
    thumbs = "".join(f'<img src="{img(f["images"][0]["key"], "-c")}" alt="" loading="lazy" width="120" height="180">' for f in firsts)
    block = f'''<section class="section brand-banner" style="padding:28px 0 0">
  <div class="container">
    <a class="brand-banner__card" href="{BRAND_FILE}">
      <span class="brand-banner__thumbs" aria-hidden="true">{thumbs}</span>
      <span class="brand-banner__copy"><span class="eyebrow">Shop by brand</span><b>{BRAND}</b><span>{len(ITEMS)} suits, tuxedos, dress pants and jackets in {len(ORDERED)} product types, from {money(lo)}.</span></span>
      <span class="brand-banner__go">Shop {BRAND} &rarr;</span>
    </a>
  </div>
</section>'''
    path = os.path.join(ROOT, "king.html")
    src = open(path, encoding="utf-8").read()
    open(path, "w", encoding="utf-8").write(replace_between(src, "<!-- BRANDS:START -->", "<!-- BRANDS:END -->", block))


def main():
    build_brand()
    for s in ORDERED:
        build_type(s)
    for it in ITEMS:
        build_product(it)
    build_king_products()
    build_king_banner()
    print("antonio-uomo:", len(ORDERED), "type pages,", len(ITEMS), "product pages")
    import gen_nav
    gen_nav.main()


if __name__ == "__main__":
    main()
