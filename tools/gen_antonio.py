"""Builds the Antonio Uomo section under Men (King) from tools/catalog/antonio-uomo.json (made by tools/au_fetch.py).

  antonio-uomo.html                         the brand page: one card per product type
  antonio-uomo-<type>.html                  a product-type page (e.g. 2 Piece Slim Fit Single Breasted Suits): every colour, with a colour filter
  antonio-uomo-<style>-<colour>-<code>.html  one page per colour ("Indigo 2 Piece Slim Fit Single Breasted Suit"): photos, price, size picker, details and a pop-up size chart (the chart the supplier shows for that product)

The ten pieces from tools/catalog/king.json ("The Openings": The Sicilian, The Ruy Lopez…) are Antonio Uomo products too, so they live here as a
product type of their own, with the same pages and the same sizing/product information (tools/suit_info.py). king.html ("Shop all men") is
generated here as well: every Antonio Uomo piece in one filterable grid. Run:  python3 tools/gen_antonio.py   (gen_nav.py runs at the end).
"""
import os, json, re, html
from gen_pawn_pages import HEADER, FOOTER, ANNOUNCE, CSS_VERSION, FAVICON, page_head
from gen_info_pages import glyph_defs
from shoplib import shop_block, replace_between, esc
import au_sizes
import suit_info
from suit_info import DESIGN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AU_ITEMS = json.load(open(os.path.join(ROOT, "tools", "catalog", "antonio-uomo.json"), encoding="utf-8"))
for _a in AU_ITEMS:                                    # file every scraped piece under our categories (tools/suit_info.py CATEGORIES)
    _a["type"] = suit_info.category_for(_a["style"])
    _a["type_slug"] = re.sub(r"[^a-z0-9]+", "-", _a["type"].lower()).strip("-")
BRAND = "Antonio Uomo"
BRAND_FILE = "antonio-uomo.html"
ASSET = "assets/img/antonio-uomo/"

TYPE_ORDER = [re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") for label, _ in suit_info.CATEGORIES]
BLURB = {
    "2-piece-slim-fit-suits": "Jacket and trousers in a modern slim cut, for weddings, school events and work.",
    "3-piece-slim-fit-suits": "Jacket, vest and trousers in a slim, contemporary cut.",
    "3-piece-classic-fit-suits": "Jacket, vest and trousers in a roomier classic cut, with sizes up to 62.",
    "plaid-suits": "Slim-fit three-piece suits in plaid.",
    "textured-suits": "Slim-fit three-piece suits in textured and shiny fabrics.",
    "2-piece-tuxedo": "Slim-fit tuxedo jacket and trousers for black tie, prom and weddings.",
    "3-piece-tuxedo": "Slim-fit tuxedos with jacket, vest and trousers, plus a double-breasted style.",
    "jackets": "Shiny patterned jackets, a standout piece for any formal occasion.",
    "pants": "Stretch dress pants with a flat front and a slim, straight leg.",
}
FAMILY_ORDER = ["Black", "Charcoal", "Grey", "Silver", "Navy", "Blue", "Teal", "Green", "Burgundy", "Red", "Pink", "Purple", "Brown", "Beige", "Gold", "White", "Other"]
FACETS = [{"key": "color", "label": "Colour", "swatch": True}, {"key": "style", "label": "Style"}, {"key": "pattern", "label": "Pattern"}, {"key": "occasion", "label": "Occasion"}]
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



# The ten chess-named pieces from tools/catalog/king.json are Antonio Uomo products: each is filed under a regular category and named like the rest
# ("<Colour> <Style name>"); its chess name and notation stay on the page and card where the supplier's style number would be.
OPENING_AS = {
    "sicilian-onyx-tux": ("Black", "2 Piece Slim Fit Tuxedo"), "ruy-lopez-three-piece": ("Black", "3 Piece Slim Fit Suit"),
    "caro-kann-navy-plaid": ("Navy", "3 Piece Plaid Suit"), "kings-gambit-royal-plaid": ("Royal Blue", "3 Piece Plaid Suit"),
    "english-opening-charcoal": ("Charcoal", "2 Piece Slim Fit Single Breasted Suit"), "queens-gambit-graphite": ("Graphite", "2 Piece Slim Fit Tuxedo"),
    "london-system-stone": ("Stone", "3 Piece Slim Fit Suit"), "italian-game-bordeaux": ("Bordeaux", "2 Piece Slim Fit Tuxedo"),
    "french-defense-slate-check": ("Slate", "3 Piece Plaid Suit"), "scotch-game-dove-grey": ("Dove Grey", "3 Piece Slim Fit Suit"),
}


def opening_items():
    cat = json.load(open(os.path.join(ROOT, "tools", "catalog", "king.json"), encoding="utf-8"))["products"]
    out = []
    for p in cat:
        colour, style = OPENING_AS[p["slug"]]
        ty = suit_info.category_for(style)
        out.append(dict(slug=p["slug"], id=f"king/{p['slug']}", file=f"antonio-uomo-{p['slug']}.html", name=f"{colour} {style}", colour=colour, code=p["name"], notation=p["notation"],
                        code_label="Opening", style=style, type=ty, type_slug=re.sub(r"[^a-z0-9]+", "-", ty.lower()).strip("-"), family={"Cream": "Beige"}.get(p["color"], p["color"]),
                        facets=dict(style=p["style"], pattern=p["pattern"], occasion="|".join(p["occasion"]) if isinstance(p["occasion"], list) else p["occasion"]),
                        price=p["price"], pieces=int(style[0]), paras=[suit_info.LEDE], bullets=suit_info.BULLETS, sizes=suit_info.SIZES, lengths=suit_info.LENGTHS, chart=suit_info.CHART_ID,
                        images=[dict(path=f"assets/img/products/{p['slug']}.jpg", w=900, h=1350)]))
    return out


# --- filters: Style / Pattern / Occasion for every piece. The ten pieces from king.json carry their own; the scraped pieces get them from their category and
# colour (first-pass guesses, like the original King attributes — refine freely: STYLE_OF / pattern_of / occasions_of below).
STYLE_OF = {"2 Piece Slim Fit Suits": "Two-piece", "3 Piece Slim Fit Suits": "Three-piece", "3 Piece Classic Fit Suits": "Three-piece", "Plaid Suits": "Three-piece",
            "Textured Suits": "Three-piece", "2 Piece Tuxedo": "Tuxedo", "3 Piece Tuxedo": "Tuxedo", "Jackets": "Jacket", "Pants": "Pants"}
CLASSIC_COLOURS = {"Black", "Navy", "Charcoal", "Grey", "White", "Burgundy", "Silver"}


def pattern_of(it):
    ty = it["type"]
    if ty == "Plaid Suits":
        return "Plaid"
    if ty == "Textured Suits":
        return "Textured"
    if ty == "Jackets":
        return "Patterned"
    return "Shiny" if "shiny" in it["colour"].lower() else "Solid"


def occasions_of(it):
    ty, fam, col = it["type"], it["family"], it["colour"].lower()
    shiny = "shiny" in col
    light = fam in ("Beige", "White") or any(w in col for w in ("light", "powder", "sky", "stone", "cream"))
    if ty in ("2 Piece Tuxedo", "3 Piece Tuxedo"):
        occ = ["Wedding", "Prom"]
        return (["Black tie"] if fam in CLASSIC_COLOURS else []) + occ
    if ty == "Textured Suits":
        return ["Wedding", "Prom"] if shiny else ["Wedding", "Prom", "Formal"] + ([] if light else ["Business"])
    if ty == "Jackets":
        return ["Prom", "Formal"]
    if ty == "Pants":
        return ["Business", "Formal"]
    return ["Business", "Wedding", "Formal"] + (["Summer"] if light else [])   # slim / classic / plaid suits


for _a in AU_ITEMS:
    _a["facets"] = dict(style=STYLE_OF[_a["type"]], pattern=pattern_of(_a), occasion="|".join(occasions_of(_a)))
ITEMS = opening_items() + AU_ITEMS
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


def card(it, extra="", facets=True):
    pic = img_url(it["images"][0], "-c")
    fx = "".join(f' data-f-{k}="{esc(v)}"' for k, v in it.get("facets", {}).items()) if facets else ""
    return f'''            <a class="product-card au-card" href="{pfile(it)}" data-id="{it.get("id", "antonio-uomo/" + it["slug"])}" data-name="{esc(it["name"])}" data-tag="{esc(it["type"])}" data-price="{money(it["price"])[1:]}" data-img="{pic}" data-f-color="{it["family"]}"{fx}{extra}>
              <span class="au-card__img"><img src="{pic}" alt="{esc(it["name"])}" loading="lazy" width="480" height="720"></span>
              <div class="product-card__meta"><div><h4>{esc(it.get("colour", it["name"]))}</h4><span class="piece-tag">{esc(it["style"])} &middot; {esc(it["code"])}</span></div><span class="product-card__price">{money(it["price"])}</span></div>
            </a>'''


def cats_nav(active):
    """Category pills under the page header: Shop All + every Antonio Uomo category (same labels as the menu)."""
    links = [(BRAND_FILE, "Shop All", active == "all")] + [(tfile(s), TYPES[s][0]["type"], s == active) for s in ORDERED]
    on_attr = ' class="is-on" aria-current="page"'
    pills = "".join(f'<a href="{h}"{on_attr if on else ""}>{esc(l)}</a>' for h, l, on in links)
    return f'<nav class="au-cats" aria-label="Antonio Uomo categories"><div class="container">{pills}</div></nav>'


def sort_key(i):
    return (ORDERED.index(i["type_slug"]) if i["type_slug"] in ORDERED else 99, FAMILY_ORDER.index(i["family"]) if i["family"] in FAMILY_ORDER else 99, i["colour"], i["code"])


def build_brand():
    """Shop All: every Antonio Uomo piece in one grid (no hero: that is for main categories)."""
    total = len(ITEMS)
    lo, hi = price_range(ITEMS)
    facets = FACETS
    cards = "\n".join(card(i) for i in sorted(ITEMS, key=sort_key))
    shop_html = shop_block(cards, facets, "au", count_noun="pieces", review_facets=[])
    head = page_head(crumbs(*BASE_CRUMBS), esc(BRAND), f"Suits, tuxedos, jackets and pants: {total} pieces from {money(lo)}.")
    body = f"{head}\n{cats_nav('all')}\n{shop_html}"
    write(BRAND_FILE, shell(f"{BRAND} — Men's Suits & Tuxedos | Checkmatela", f"Antonio Uomo men's suits, tuxedos, jackets and pants at Checkmatela: {total} pieces from {money(lo)}.", body,
                            extra_js='<script src="js/shop.js?v=4"></script>'))


def build_type(slug):
    its = sorted_items(TYPES[slug])
    name = its[0]["type"]
    lo, hi = price_range(its)
    lead = f"{len(its)} piece{'s' if len(its) != 1 else ''}, {'from ' + money(lo) if lo != hi else money(lo)}. {BLURB.get(slug, '')}"
    facets = FACETS
    cards = "\n".join(card(i) for i in its)
    shop_html = shop_block(cards, facets, "au", count_noun="pieces", review_facets=[])
    head = page_head(crumbs(*BASE_CRUMBS, (name, tfile(slug))), esc(name), esc(lead))
    body = f"{head}\n{cats_nav(slug)}\n{shop_html}"
    write(tfile(slug), shell(f"{name} — {BRAND} | Checkmatela", f"{name} by {BRAND}: {len(its)} pieces, {'from ' + money(lo) if lo != hi else money(lo)}. Browse colors and sizes at Checkmatela.", body,
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
    opening = bool(it.get("code_label"))                  # a piece from tools/catalog/king.json ("The Openings") keeps its own name, style and notation
    codeline = f"{esc(it['code'])} &middot; {it['code_label']} {esc(it['notation'])} &middot; {esc(tname)}" if opening else f"Style {esc(it['code'])} &middot; {esc(tname)}"
    body = pdp_body(it, eyebrow=f"{BRAND} &middot; Men", codeline=codeline, tag=it.get("tag") or f"{BRAND} · {it['style']}",
                    crumb_parts=[*BASE_CRUMBS, (tname, tfile(slug)), (it["name"], pfile(it))], related_html=rel_html)
    write(pfile(it), shell(f"{it['name']} ({it['code']}) — {BRAND} | Checkmatela",
                           f"{it['name']} ({it['code']}) by {BRAND}, {money(it['price'])}. " if opening else f"{it['name']} by {BRAND}, style {it['code']}, {money(it['price'])}. " + (it["bullets"][0] + ". " if it["bullets"] else "") + "Sizes, details and size chart at Checkmatela.",
                           body, extra_js='<script src="js/product.js?v=5"></script>'))


def category_of(it):
    n = it["type"]
    return "Tuxedos" if "Tuxedo" in n else "Pants" if "Pants" in n else "Jackets" if "Jacket" in n else "Suits"


def build_king_page():
    """king.html = Shop all men: every Antonio Uomo piece in one grid, filtered by colour, style, pattern, occasion and price."""
    facets = FACETS
    cards = "\n".join(card(i) for i in sorted(ITEMS, key=sort_key))
    block = shop_block(cards, facets, "au-all", count_noun="pieces", review_facets=[], extra_attrs=' data-aggregate="1"')
    path = os.path.join(ROOT, "king.html")
    src = open(path, encoding="utf-8").read()
    src = replace_between(src, "<!-- SHOP:START -->", "<!-- SHOP:END -->", block)
    src = src.replace("js/shop.js?v=", "js/shop.js?v=") if "js/shop.js" in src else src.replace('<script src="js/main.js"></script>', '<script src="js/main.js"></script>\n<script src="js/shop.js?v=4"></script>')
    open(path, "w", encoding="utf-8").write(src)


def main():
    build_brand()
    for s in ORDERED:
        build_type(s)
    for it in ITEMS:
        build_product(it)
    build_king_page()
    wanted = {BRAND_FILE} | {tfile(s) for s in ORDERED} | {pfile(i) for i in ITEMS}      # every antonio-uomo-*.html is generated: drop pages of categories that no longer exist
    for f in os.listdir(ROOT):
        if (f == BRAND_FILE or f.startswith("antonio-uomo-")) and f.endswith(".html") and f not in wanted:
            os.remove(os.path.join(ROOT, f))
    print("antonio-uomo:", len(ORDERED), "type pages,", len(ITEMS), "product pages")
    import gen_nav
    gen_nav.main()


if __name__ == "__main__":
    main()
