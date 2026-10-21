"""Builds the Gioberti catalog (tools/catalog/gioberti.json, made by tools/gb_fetch.py) into the Men and Kids departments, split by dress code:

  Men  -> Formal         men-formal.html          (existing suits/tuxedos + Blazers & Sport Coats, Suit Vests, Dress Shirts, Dress Pants, Accessories)
       -> Not So Formal  men-not-so-formal.html   (Gioberti's own casual categories: Casual Shirts, Flannel, Polos, Sweaters, Hoodies, Jackets, …)
  Kids -> Formal         boys-formal.html         (existing Magen Kids cuts + Suits & Blazers, Suit Vests, Dress Shirts, Dress Pants, Accessories)
       -> Not So Formal  boys-not-so-formal.html
  men-<category>.html / boys-<category>.html      one filterable grid per category (no hero: subcategory pages use the compact page head)
  gioberti-<handle>.html                          one page per product: photos, colour + size pickers (sold-out combinations disabled, the photo
                                                  follows the colour), price, details and that product's own size chart pop-up
  bishop.html                                     formal accessories (cummerbund and suspender sets) go in the existing Accessories grid,
                                                  between <!-- GIOBERTI:START/END --> markers
  king.html / pawn.html                           a Formal / Not So Formal category bar under the intro (<!-- DRESSCODE:START/END -->)

The Men / Kids menus (js/nav.js MEGA) list these as three closed dropdowns: Formal, Not So Formal and Occasion.
Prices are Gioberti's listed prices, copied as placeholders (like Antonio Uomo); the "was" prices are not copied.
Run:  python3 tools/gen_gioberti.py   (gen_nav.py runs at the end). Refresh the catalog first with  python3 tools/gb_fetch.py
"""
import os, re, json
from gen_antonio import shell, crumbs, write, acc, money
from gen_pawn_pages import page_head
from shoplib import shop_block, replace_between, esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = json.load(open(os.path.join(ROOT, "tools", "catalog", "gioberti.json"), encoding="utf-8"))
BRAND = "Gioberti"
ASSET = "assets/img/gioberti/"

DEPTS = {
    "men": dict(label="Men", crumb=("Men", "king.html"), glyph="glyph-king", formal="men-formal.html", nsf="men-not-so-formal.html", sub="King"),
    "boys": dict(label="Boys", crumb=("Kids", "pawn.html"), glyph="glyph-pawn", formal="boys-formal.html", nsf="boys-not-so-formal.html", sub="Pawn"),
}
GROUP_LABEL = {"formal": "Formal", "nsf": "Not So Formal"}

# category key -> (department, group, label, one-line description). Order = order in menus, pills and landing pages.
CATS = {
    "men-blazers": ("men", "formal", "Blazers & Sport Coats", "Formal, velvet and linen blazers to wear with suit pants or over a dress shirt."),
    "men-suit-vests": ("men", "formal", "Suit Vests & Vest Sets", "Five- and six-button suit vests in tweed, solids and pinstripes, plus four-piece vest sets with ties."),
    "men-dress-shirts": ("men", "formal", "Dress Shirts", "Long and short sleeve dress shirts and tuxedo shirt sets."),
    "men-dress-pants": ("men", "formal", "Dress Pants", "Formal dress pants, including expandable-waist styles."),
    "men-casual-shirts": ("men", "nsf", "Casual Shirts", "Button-down twill and casual shirts for weekends and smart-casual days."),
    "men-flannel-shirts": ("men", "nsf", "Flannel Shirts", "Soft brushed flannels for cooler days."),
    "men-polo-shirts": ("men", "nsf", "Polo Shirts", "Short sleeve striped and solid polos."),
    "men-sweaters": ("men", "nsf", "Sweaters", "Knitted cardigans, pullovers and sweaters."),
    "men-hoodies": ("men", "nsf", "Hoodies", "Everyday hoodies and sweatshirts."),
    "men-jackets": ("men", "nsf", "Jackets", "Cargo, twill and bomber jackets."),
    "men-outerwear": ("men", "nsf", "Outerwear", "Coats and layers for cold weather."),
    "men-leather-jackets": ("men", "nsf", "Leather Jackets", "Leather and faux leather jackets."),
    "men-activewear": ("men", "nsf", "Activewear", "Athletic shorts, joggers and track pants."),
    "men-sleepwear": ("men", "nsf", "Sleepwear", "Pajamas and loungewear."),
    "men-accessories": ("men", "nsf", "Accessories", "Ivy caps, sandals and everyday extras."),
    "boys-suits-blazers": ("boys", "formal", "Suits & Blazers", "Formal suit sets, blazer and pants sets, and velvet, corduroy and tweed blazers."),
    "boys-suit-vests": ("boys", "formal", "Suit Vests & Vest Sets", "Suit vests, vest and pants sets, and four-piece vest sets with ties."),
    "boys-dress-shirts": ("boys", "formal", "Dress Shirts", "Dress shirts, shirt and tie sets, and tuxedo shirt sets."),
    "boys-dress-pants": ("boys", "formal", "Dress Pants", "Adjustable-waist dress pants, including husky sizes."),
    "boys-casual-shirts": ("boys", "nsf", "Casual Shirts", "Button-down and casual shirts for school and weekends."),
    "boys-polo-shirts": ("boys", "nsf", "Polo Shirts", "Polos and t-shirts."),
    "boys-sweaters": ("boys", "nsf", "Sweaters", "Cardigans, sweater vests and pullovers."),
    "boys-jackets": ("boys", "nsf", "Jackets", "Everyday jackets."),
    "boys-activewear": ("boys", "nsf", "Activewear", "Athletic shorts, joggers and track sets."),
    "boys-shorts": ("boys", "nsf", "Casual Shorts", "Casual shorts for warm days."),
    "boys-sleepwear": ("boys", "nsf", "Sleepwear", "Pajamas and loungewear."),
    "boys-accessories": ("boys", "nsf", "Accessories", "Ivy caps and everyday extras."),
}
# Gioberti product type -> our category
TYPE_MAP = {
    "Mens Suits & Sport Coats": "men-blazers", "Mens Formal Vests": "men-suit-vests", "Mens Dress Shirts": "men-dress-shirts", "Mens Dress Pants": "men-dress-pants",
    "Mens Casual Shirt": "men-casual-shirts", "Mens Flannel Shirts": "men-flannel-shirts", "Mens Polo Shirts": "men-polo-shirts", "Mens Sweaters": "men-sweaters",
    "Mens Hoodies": "men-hoodies", "Mens Jackets": "men-jackets", "Mens Outerwear": "men-outerwear", "Mens Leather Jacket": "men-leather-jackets",
    "Mens Active Wear": "men-activewear", "Mens": "men-activewear", "Mens Sleepwear": "men-sleepwear", "Mens Accessories": "men-accessories",
    "Boys Blazers": "boys-suits-blazers", "Boys Suit Vest": "boys-suit-vests", "Boys Dress Shirts": "boys-dress-shirts", "Boys Dress Pants": "boys-dress-pants",
    "Boys Button Down Shirts": "boys-casual-shirts", "Boys Polos and T-Shirts": "boys-polo-shirts", "Boys Sweaters": "boys-sweaters", "Boys Jackets": "boys-jackets",
    "Boys Active Wear": "boys-activewear", "Boys Shorts": "boys-shorts", "Boys Sleepwear": "boys-sleepwear", "Boys Accessories": "boys-accessories",
}
BISHOP = "bishop"                          # formal accessories -> the existing Accessories page


def category_of(it):
    h = it["handle"]
    if re.search(r"cumberbund|cummerbund|suspender", h):
        return BISHOP
    if h.startswith("si-501"):            # filed by Gioberti under dress shirts, but they are casual twill shirts
        return "men-casual-shirts"
    return TYPE_MAP.get(it["ptype"])


for _it in ITEMS:
    _it["cat"] = category_of(_it)
    _it["file"] = f"gioberti-{_it['handle']}.html"
    _it["dept"] = ("boys" if re.match(r"(cm-8|susk)", _it["handle"]) else "men") if _it["cat"] == BISHOP else (CATS[_it["cat"]][0] if _it["cat"] else None)
UNFILED = [i for i in ITEMS if not i["cat"]]
ITEMS = [i for i in ITEMS if i["cat"]]
BY_CAT = {}
for _it in ITEMS:
    BY_CAT.setdefault(_it["cat"], []).append(_it)
ACCESSORIES = BY_CAT.get(BISHOP, [])

# Formal pages that already exist on the site, listed first in each Formal list (label, url)
FORMAL_EXISTING = {
    "men": [("Two-piece suits", "king.html?style=Two-piece"), ("Three-piece suits", "king.html?style=Three-piece"), ("Tuxedos", "king.html?style=Tuxedo")],
    "boys": [("Suits", "pawn-slim-fit.html"), ("Tuxedos", "pawn-tuxedo.html"), ("Husky fit", "pawn-husky.html"), ("Ring bearer", "pawn-ring-bearer.html")],
}
# Antonio Uomo pieces (already on king.html) that also belong on a men's formal category page: category -> king.html Style facet
FROM_KING = {"men-blazers": "Jacket", "men-dress-pants": "Pants"}


def img(key, kind=""):
    return f"{ASSET}{key}{kind}.webp"


def photos(it):
    return [im for im in it["images"] if not im["chart"] and im.get("key")]


def cover(it):
    """Card photo: the first in-stock colour's own photo, else the first photo."""
    key = next((it["colour_img"][c] for c in it["colours"] if c in it["colour_img"]), None)
    return key or (photos(it) or it["images"])[0]["key"]


def price_text(it):
    return money(it["price"]) if it["price"] == it["price_max"] else "From " + money(it["price"])


def cat_files(dept, group):
    return [k for k, v in CATS.items() if v[0] == dept and v[1] == group and BY_CAT.get(k)]


def card(it, with_cat=False):
    pic = img(cover(it), "-c")
    n = len(it["colours"])
    label = "Accessories" if it["cat"] == BISHOP else CATS[it["cat"]][2]
    fx = f' data-f-color="{esc("|".join(it["families"]))}" data-f-brand="{BRAND}"' + (f' data-f-category="{esc(label)}"' if with_cat else "")
    return f'''            <a class="product-card au-card" href="{it["file"]}" data-id="gioberti/{it["handle"]}" data-name="{esc(it["name"])}" data-tag="{esc(label)}" data-price="{it["price"]:g}" data-img="{pic}"{fx}>
              <span class="au-card__img"><img src="{pic}" alt="{esc(it["name"])}" loading="lazy" width="480" height="640"></span>
              <div class="product-card__meta"><div><h4>{esc(it["name"])}</h4><span class="piece-tag">{esc(label)}{f" &middot; {n} colours" if n > 1 else ""}</span></div><span class="product-card__price">{price_text(it)}</span></div>
            </a>'''


def king_cards(style):
    """The Antonio Uomo cards of one Style from king.html (generated by gen_antonio.py), tagged with their brand for the Brand filter."""
    src = open(os.path.join(ROOT, "king.html"), encoding="utf-8").read()
    out = re.findall(r'[ \t]*<a class="product-card au-card"[^>]*data-f-style="' + style + r'"[^>]*>.*?</a>', src, re.S)
    return [re.sub(r' data-f-style="[^"]*"', ' data-f-brand="Antonio Uomo"', c) for c in out]


def pills(dept, group, active):
    d = DEPTS[dept]
    landing = d[group]
    links = [(landing, f"All {GROUP_LABEL[group].lower()}")]                     # (href, label)
    if group == "formal":
        links += [(u, l) for l, u in FORMAL_EXISTING[dept]]
    links += [(f"{k}.html", CATS[k][2]) for k in cat_files(dept, group)]
    if group == "formal":
        links.append(("bishop.html", "Accessories"))
    on =' class="is-on" aria-current="page"'
    return f'<nav class="au-cats" aria-label="{GROUP_LABEL[group]} categories"><div class="container">' + "".join(
        f'<a href="{h}"{on if h == active else ""}>{esc(l)}</a>' for h, l in links) + "</div></nav>"


def dept_crumbs(dept, group, *more):
    d = DEPTS[dept]
    return [("Home", "index.html"), d["crumb"], (GROUP_LABEL[group], d[group]), *more]


SHOP_JS = '<script src="js/shop.js?v=6"></script>'


def build_category(key):
    dept, group, label, blurb = CATS[key]
    d = DEPTS[dept]
    its = BY_CAT[key]
    cards = [card(i) for i in its]
    facets = [{"key": "color", "label": "Colour", "swatch": True}]
    if key in FROM_KING:
        cards += king_cards(FROM_KING[key])
        facets.append({"key": "brand", "label": "Brand"})
    lo = min(i["price"] for i in its)
    title = f"{d['label']}'s {label}"
    head = page_head(crumbs(*dept_crumbs(dept, group, (label, f"{key}.html"))), esc(title), f"{esc(blurb)} {len(cards)} pieces from {money(lo)}.")
    body = f"{head}\n{pills(dept, group, key + '.html')}\n{shop_block(chr(10).join(cards), facets, 'gioberti', count_noun='pieces', review_facets=[])}"
    write(f"{key}.html", shell(f"{title} — {GROUP_LABEL[group]} | Checkmatela", f"{title} at Checkmatela: {len(cards)} pieces from {money(lo)}. {blurb}",
                               body, glyph=d["glyph"], extra_js=SHOP_JS))
    return dict(key=key, label=label, n=len(cards), lo=lo, img=img(cover(its[0]), "-c"))


def style_card(href, title, text, badge, photo=None, glyph=None):
    media = f'<span class="style-card__photo"><img src="{photo}" alt="" loading="lazy"></span>' if photo else \
        f'<span class="style-card__glyph"><svg viewBox="0 0 100 130" aria-hidden="true"><use href="#{glyph}" fill="currentColor"/></svg></span>'
    return f'''      <a class="style-card style-card--live" href="{href}">
        {media}
        <h4>{esc(title)}</h4>
        <p>{esc(text)}</p>
        <span class="style-card__badge style-card__badge--live">{esc(badge)} →</span>
      </a>'''


def build_landing(dept, group, built):
    d = DEPTS[dept]
    page = d[group]
    who = d["label"].lower()
    tiles = []
    if group == "formal":
        tiles += [style_card(u, l, f"Browse the full {l.lower()} collection.", f"Shop {l.lower()}", glyph=d["glyph"]) for l, u in FORMAL_EXISTING[dept]]
    tiles += [style_card(f"{b['key']}.html", b["label"], f"{b['n']} pieces from {money(b['lo'])}.", f"Shop {b['label'].lower()}", photo=b["img"]) for b in built if CATS[b["key"]][0] == dept and CATS[b["key"]][1] == group]
    if group == "formal":
        tiles.append(style_card("bishop.html", "Accessories", "Cummerbunds, suspenders, bow ties, pocket squares and cufflinks.", "Shop accessories", glyph=d["glyph"]))
        lead = f"Everything for the formal occasion: suits, tuxedos, blazers, vests, dress shirts and dress pants for {who}."
        h2 = "Dressed for the occasion."
    else:
        lead = f"Everyday and off-duty pieces for {who}: shirts, sweaters, jackets, activewear and more, for when the dress code is relaxed."
        h2 = "Relaxed, not careless."
    title = f"{d['label']}'s {GROUP_LABEL[group]}"
    head = page_head(crumbs(*dept_crumbs(dept, group)), esc(title), esc(lead))
    grid = ""
    if group == "nsf":
        its = [i for k in cat_files(dept, "nsf") for i in BY_CAT[k]]
        grid = shop_block("\n".join(card(i, with_cat=True) for i in its), [{"key": "category", "label": "Category"}, {"key": "color", "label": "Colour", "swatch": True}],
                          "gioberti", count_noun="pieces", review_facets=[])
    body = f'''{head}
{pills(dept, group, page)}
<section class="section" style="padding-top:36px;padding-bottom:{"0" if grid else "64px"}">
  <div class="container">
    <div class="section-head"><span class="eyebrow">Shop by category</span><h2>{h2}</h2></div>
    <div class="style-grid">
{chr(10).join(tiles)}
    </div>
  </div>
</section>
{grid}'''
    write(page, shell(f"{title} | Checkmatela", f"{title} at Checkmatela. {lead}", body, glyph=d["glyph"], extra_js=SHOP_JS if grid else ""))


def gallery(it):
    ims = photos(it)
    first_key = cover(it)
    first = next((im for im in ims if im["key"] == first_key), ims[0])
    thumbs = "".join(f'<button type="button" class="pdp-thumb{" is-active" if im is first else ""}" data-src="{img(im["key"])}" data-w="{im["w"]}" data-h="{im["h"]}" aria-label="Show photo {n} of {len(ims)}"><img src="{img(im["key"], "-t")}" alt="" loading="lazy" width="72" height="72"></button>'
                     for n, im in enumerate(ims, 1))
    main = f'<img id="pdpMain" src="{img(first["key"])}" alt="{esc(it["name"])}" width="900" height="{round(900 * first["h"] / first["w"])}" fetchpriority="high">'
    return f'<div class="pdp-gallery"><div class="pdp-main" id="pdpFrame" style="--r:{first["w"] / first["h"]:.4f}">{main}</div>{f"<div class=pdp-thumbs>{thumbs}</div>" if len(ims) > 1 else ""}</div>'.replace("<div class=pdp-thumbs>", '<div class="pdp-thumbs">')


def option_chips(it):
    """One chip group per option (colour first). Only values with at least one in-stock variant; a colour chip carries its own photo."""
    dims = {im["key"]: im for im in it["images"] if im.get("key")}
    out = []
    for oi, o in enumerate(it["options"]):
        vals = [v for v in o["values"] if any(r[oi] == v and r[-1] for r in it["variants"])]
        btns = []
        for v in vals:
            extra = ""
            if oi == 0 and v in it["colour_img"] and it["colour_img"][v] in dims:
                im = dims[it["colour_img"][v]]
                extra = f' data-img="{img(im["key"])}" data-w="{im["w"]}" data-h="{im["h"]}"'
            btns.append(f'<button type="button" class="chip-btn" data-v="{esc(v)}"{extra} aria-pressed="{"true" if len(vals) == 1 else "false"}">{esc(v)}</button>')
        key = re.sub(r"[^a-z]", "", o["name"].lower()) or "option"
        out.append(f'<fieldset class="pdp-opt" data-key="{key}"><legend>{esc(o["name"])}</legend><div class="pdp-chips">{"".join(btns)}</div></fieldset>')
    return "\n        ".join(out)


CHART_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M3 15 15 3l6 6L9 21z"/><path d="M7 11l2 2M10 8l2 2M13 5l2 2M5 13l1 1"/></svg>'


def build_product(it):
    cat = it["cat"]
    if cat == BISHOP:
        label, parts, eyebrow, more_href = "Accessories", [("Home", "index.html"), ("Accessories", "bishop.html"), (it["name"], it["file"])], f"{BRAND} &middot; Accessories", "bishop.html"
        related = [i for i in ACCESSORIES if i is not it][:4]
    else:
        dept, group, label, _ = CATS[cat]
        parts = dept_crumbs(dept, group, (label, f"{cat}.html"), (it["name"], it["file"]))
        eyebrow, more_href = f"{BRAND} &middot; {DEPTS[dept]['label']} &middot; {GROUP_LABEL[group]}", f"{cat}.html"
        related = [i for i in BY_CAT[cat] if i is not it][:4]
    chart = next((im for im in it["images"] if im["chart"] and im.get("key")), None)
    chart_btn = f'<button type="button" class="pdp-chart-btn" data-open-chart aria-haspopup="dialog">{CHART_ICON}Size chart</button>' if chart else ""
    chart_dialog = (f'<dialog class="shop-dialog au-chart" id="sizeChart" aria-labelledby="gbChartTitle"><button type="button" class="shop-dialog__x" aria-label="Close size chart">×</button>'
                    f'<div class="au-chart__body"><h2 class="au-chart__title" id="gbChartTitle">{esc(it["name"])} size chart</h2><img class="gb-chart" src="{img(chart["key"], "-z")}" alt="{esc(it["name"])} size chart" loading="lazy" width="{min(1400, chart["w"])}" height="{round(min(1400, chart["w"]) * chart["h"] / chart["w"])}">'
                    f'<p class="au-size__note">Measurements from {BRAND}, for this product. Not sure between two sizes? <a class="link" href="book-a-fitting.html?look={esc(it["name"].replace(" ", "%20"))}">Ask us about fit</a>.</p></div></dialog>') if chart else ""
    n = len(it["colours"])
    lede = f"{it['name']} by {BRAND}" + (f", in {n} colours." if n > 1 else ".") + " Choose your options, then add it to your preview bag or ask us about fit."
    details = (f'<ul class="pdp-list">{"".join(f"<li>{esc(b)}</li>" for b in it["bullets"])}</ul>' if it["bullets"] else "") + "".join(f"<p>{esc(p)}</p>" for p in it["paras"])
    variants = json.dumps({"n": len(it["options"]), "v": it["variants"]}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    rel = ""
    if related:
        rel = f'''<section class="section pdp-related">
  <div class="container">
    <div class="section-head"><span class="eyebrow">More like this</span><h2>{esc(label)}</h2></div>
    <div class="product-grid">
{chr(10).join(card(r) for r in related)}
    </div>
    <p style="text-align:center;margin-top:28px"><a class="btn dark-ghost" href="{more_href}">See all {esc(label.lower())}</a></p>
  </div>
</section>'''
    body = f'''<main class="pdp" id="pdp" data-id="gioberti/{it["handle"]}" data-name="{esc(it["name"])}" data-tag="{BRAND} · {esc(label)}" data-price="{it["price"]:g}" data-img="{img(cover(it), "-c")}">
  <div class="container">
    {crumbs(*parts).replace('class="crumbs"', 'class="crumbs crumbs--light"')}
    <div class="pdp__grid">
      {gallery(it)}
      <div class="pdp-info">
        <span class="eyebrow">{eyebrow}</span>
        <h1>{esc(it["name"])}</h1>
        <p class="pdp-code">Style {esc(it["code"])} &middot; {esc(label)}</p>
        <p class="pdp-price">{price_text(it)}</p>
        <p class="pdp-lede">{esc(lede)}</p>
        {option_chips(it)}
        {chart_btn}
        <p class="pdp-msg" role="status"></p>
        <div class="pdp-cta"><button type="button" class="btn pdp-add">Add to preview bag</button><a class="btn dark-ghost" href="book-a-fitting.html?look={esc(it["name"].replace(" ", "%20"))}">Ask about fit</a></div>
        <p class="pdp-assure"><a href="shipping-returns.html">Free exchanges and easy returns</a></p>
        <p class="pdp-fine">Preview only: prices and availability are not confirmed, and checkout is not connected.</p>
        <div class="pdp-accs">
          {acc("Details", details, True)}
        </div>
      </div>
    </div>
  </div>
  {chart_dialog}
  <script type="application/json" id="pdpVariants">{variants}</script>
</main>

{rel}'''
    glyph = "glyph-pawn" if it["dept"] == "boys" else "glyph-king"
    write(it["file"], shell(f"{it['name']} ({it['code']}) — {BRAND} | Checkmatela", f"{it['name']} by {BRAND}, style {it['code']}, {price_text(it)}. Colours, sizes, details and size chart at Checkmatela.",
                            body, glyph=glyph, extra_js='<script src="js/product.js?v=6"></script>'))


def stamp_bishop():
    path = os.path.join(ROOT, "bishop.html")
    src = open(path, encoding="utf-8").read()
    block = "\n".join(card(i) for i in ACCESSORIES)
    if "<!-- GIOBERTI:START -->" not in src:
        src = src.replace('<div class="product-grid" data-reveal-group>', '<div class="product-grid" data-reveal-group>\n<!-- GIOBERTI:START -->\n<!-- GIOBERTI:END -->', 1)
    src = replace_between(src, "<!-- GIOBERTI:START -->", "<!-- GIOBERTI:END -->", block)
    n = len(re.findall(r'<a class="product-card[ "]', src))
    src = re.sub(r'<span class="filter-bar__count">\d+ pieces in this collection</span>', f'<span class="filter-bar__count">{n} pieces in this collection</span>', src)
    open(path, "w", encoding="utf-8").write(src)


def stamp_dresscode_bar(page, dept):
    """A Formal / Not So Formal category bar right under the department intro (king.html, pawn.html)."""
    d = DEPTS[dept]
    links = [f'<a href="{d["formal"]}"><b>Formal</b></a>'] + [f'<a href="{u}">{esc(l)}</a>' for l, u in FORMAL_EXISTING[dept]]
    links += [f'<a href="{k}.html">{esc(CATS[k][2])}</a>' for k in cat_files(dept, "formal")]
    links += [f'<a href="{d["nsf"]}"><b>Not So Formal</b></a>'] + [f'<a href="{k}.html">{esc(CATS[k][2])}</a>' for k in cat_files(dept, "nsf")]
    bar = f'<nav class="au-cats au-cats--dresscode" aria-label="Shop by dress code"><div class="container">{"".join(links)}</div></nav>'
    path = os.path.join(ROOT, page)
    src = open(path, encoding="utf-8").read()
    if "<!-- DRESSCODE:START -->" not in src:
        i = src.index("</section>", src.index('<section class="cat-intro"')) + len("</section>")
        src = src[:i] + "\n<!-- DRESSCODE:START -->\n<!-- DRESSCODE:END -->" + src[i:]
    src = replace_between(src, "<!-- DRESSCODE:START -->", "<!-- DRESSCODE:END -->", bar)
    open(path, "w", encoding="utf-8").write(src)


# --- read by gen_nav.py: search entries and department totals
def index_products():
    out = []
    for it in ITEMS:
        k, d = ("Bishop", "Accessories") if it["cat"] == BISHOP else (DEPTS[it["dept"]]["sub"], DEPTS[it["dept"]]["label"] if it["dept"] == "men" else "Kids")
        label = it["name"] if it["cat"] == BISHOP else CATS[it["cat"]][2]
        out.append(dict(k=k, d=d + " " + " ".join(it["colours"]), t=it["name"], s=f"{BRAND} · {label}", u=it["file"], p=it["price"], i=img(cover(it), "-c"), f={"color": it["families"][0]}))
    return out


def search_pages():
    pages = []
    for dept, d in DEPTS.items():
        kw = "men mens" if dept == "men" else "kids boys"
        pages.append((f"{d['label']}'s Formal", d["formal"], d["crumb"][0], f"formal suits tuxedos blazers vests dress shirts dress pants {kw}"))
        pages.append((f"{d['label']}'s Not So Formal", d["nsf"], d["crumb"][0], f"not so formal casual everyday sweaters hoodies jackets polos activewear sleepwear {kw}"))
    for k, (dept, group, label, _) in CATS.items():
        if BY_CAT.get(k):
            pages.append((f"{DEPTS[dept]['label']}'s {label}", f"{k}.html", DEPTS[dept]["crumb"][0], f"{label} {GROUP_LABEL[group]} {'men mens' if dept == 'men' else 'kids boys'} gioberti".lower()))
    return pages


def main():
    if UNFILED:
        print("WARNING: no category for", ", ".join(f"{i['handle']} ({i['ptype']})" for i in UNFILED), "- add the type to TYPE_MAP")
    built = [build_category(k) for k in CATS if BY_CAT.get(k)]
    for dept in DEPTS:
        for group in ("formal", "nsf"):
            build_landing(dept, group, built)
    for it in ITEMS:
        build_product(it)
    stamp_bishop()
    stamp_dresscode_bar("king.html", "men")
    stamp_dresscode_bar("pawn.html", "boys")
    wanted = {i["file"] for i in ITEMS}
    for f in os.listdir(ROOT):                                   # drop pages of products Gioberti no longer sells
        if f.startswith("gioberti-") and f.endswith(".html") and f not in wanted:
            os.remove(os.path.join(ROOT, f))
    print("gioberti:", len(built), "category pages, 4 landing pages,", len(ITEMS), "product pages,", len(ACCESSORIES), "on bishop.html")
    import gen_nav
    gen_nav.main()


if __name__ == "__main__":
    main()
