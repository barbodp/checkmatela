"""Builds the Gioberti catalog (tools/catalog/gioberti.json, made by tools/gb_fetch.py) into the Men and Kids departments, split by dress code:

  Men  -> Formal         men-formal.html          (existing suits/tuxedos + Blazers & Sport Coats, Suit Vests, Dress Shirts, Dress Pants, Accessories)
       -> Not So Formal  men-not-so-formal.html   (Gioberti's own casual categories: Casual Shirts, Flannel, Polos, Sweaters, Hoodies, Jackets, …)
  Kids -> Formal         boys-formal.html         (existing Magen Kids cuts + Suits & Blazers, Suit Vests, Dress Shirts, Dress Pants, Accessories)
       -> Not So Formal  boys-not-so-formal.html
  men-<category>.html / boys-<category>.html      one filterable grid per category (no hero: subcategory pages use the compact page head)
  gioberti-<handle>.html                          one page per product: photos, colour + size pickers (sold-out combinations disabled, the photo
                                                  follows the colour), price, details and that product's own size chart pop-up
  men-/boys-formal-accessories.html               cummerbund and suspender sets, men's and boys' apart; they are also on bishop.html:
                                                  men's in the main grid (<!-- GIOBERTI:START/END -->), boys' in a "For boys" section (<!-- GIOBERTI-BOYS -->)
  king.html / pawn.html                           a Formal / Not So Formal category bar under the intro (<!-- DRESSCODE:START/END -->)

The Men / Kids menus (js/nav.js MEGA) list these as three closed dropdowns: Formal, Not So Formal and Occasion.
Prices are Gioberti's listed prices, copied as placeholders (like Antonio Uomo); the "was" prices are not copied.
Run:  python3 tools/gen_gioberti.py   (gen_nav.py runs at the end). Refresh the catalog first with  python3 tools/gb_fetch.py
"""
import os, re, json
from gen_antonio import shell, crumbs, write, acc, money
from gen_pawn_pages import page_head
from shoplib import shop_block, replace_between, esc, select_opt, colour_row
from gb_catalog import CATS, TYPE_MAP, FORMAL_ACCESSORIES, CURATED, HIDDEN, HIDDEN_CATS, category_of, dept_of
from gb_fetch import families
from PIL import Image
import numpy as np
import html as htmllib
import gen_pawn_pages as pw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = json.load(open(os.path.join(ROOT, "tools", "catalog", "gioberti.json"), encoding="utf-8"))
BRAND = "Gioberti"
ASSET = "assets/img/gioberti/"

DEPTS = {
    "men": dict(label="Men", poss="Men's", crumb=("Men", "king.html"), glyph="glyph-king", formal="men-formal.html", nsf="men-not-so-formal.html", sub="King"),
    "boys": dict(label="Boys", poss="Boys'", crumb=("Kids", "pawn.html"), glyph="glyph-pawn", formal="boys-formal.html", nsf="boys-not-so-formal.html", sub="Pawn"),
}
GROUP_LABEL = {"formal": "Formal", "nsf": "Not So Formal"}

# ---------------------------------------------------------------- curated, combined listings (gb_catalog.CURATED)
SIZE_ORDER = ["X-Small", "Small", "Medium", "Large", "X-Large", "2X-Large", "3X-Large", "4X-Large", "5X-Large", "6X-Large"]
SIZE_SAME = {"XX-Large": "2X-Large", "XXX-Large": "3X-Large", "X Large": "X-Large", "2X Large": "2X-Large", "X Small": "X-Small", "Laarge": "Large"}   # one spelling per size across combined listings


def _fabric(colour):
    """'1049 - Red / Black / Gray', '1018- Navy/White', '56C - Dark Blue / Gray' -> '1049', '1018', '56'"""
    m = re.match(r"\s*(\d+)[A-Z]?\b", colour)
    return m.group(1) if m else None


def _plain(colour):
    return re.sub(r"^\s*\d+[A-Z]?\s*-\s*", "", colour).strip()


def is_solid(colour):
    """A single colour ('Heather Navy', 'Black', '52 - Night Blue'), not a plaid ('Charcoal Red', 'Red / Black', '… Check')."""
    name = _plain(colour)
    if "/" in name or re.search(r"plaid|check|line|highlight|fade|gradient|contrast|stitch|stripe", name, re.I):
        return False
    return name.lower().startswith("heather") or len(families([name])) == 1


def curate(items):
    """Replace each CURATED group of Gioberti listings by one listing holding only the chosen plaids (plus every solid when solids=True)."""
    by = {i["handle"]: i for i in items}
    used, out = set(), []
    for cfg in CURATED:
        srcs = [by[h] for h in cfg["sources"] if h in by]
        if not srcs:
            continue
        wanted, solids = cfg.get("colours"), cfg.get("solids")
        pick, solid_names = {}, []                                   # display colour -> (source item, source colour, in-stock sizes)
        for it in srcs:
            for c in it["all_colours"]:
                if wanted is None:
                    disp = c
                elif solids and is_solid(c):
                    disp = _plain(c)
                    if disp not in solid_names:
                        solid_names.append(disp)
                elif c in wanted:                                        # an exact Gioberti colour name (polos)
                    disp = wanted[c]
                elif _fabric(c) in wanted:                               # a fabric number (plaids): the number stays in the name
                    disp = f"{wanted[_fabric(c)]} ({_fabric(c)})"
                else:
                    continue
                ok = sum(1 for r in it["variants"] if r[0] == c and r[-1])
                if disp not in pick or ok > pick[disp][2]:
                    pick[disp] = (it, c, ok)
        if wanted is None:
            names = [c for it in srcs for c in it["all_colours"]]
            names = [n for i, n in enumerate(names) if n not in names[:i]]
        else:
            names = [f"{n} ({k})" if k.isdigit() else n for k, n in wanted.items()] + solid_names
        names = [n for n in names if n in pick]
        sizes = []
        for it in srcs:
            sizes += [SIZE_SAME.get(v, v) for v in it["options"][1]["values"] if SIZE_SAME.get(v, v) not in sizes]
        sizes.sort(key=lambda v: SIZE_ORDER.index(v) if v in SIZE_ORDER else 99)
        rows, images, colour_img = [], [], {}
        for n in names:
            it, c, _ = pick[n]
            rows += [[n, SIZE_SAME.get(r[1], r[1]), r[2], r[3]] for r in it["variants"] if r[0] == c]
            images += [dict(im, colours=[n]) for im in it["images"] if c in (im.get("colours") or []) and im.get("key") and not im["chart"]]
            if c in it["colour_img"]:
                colour_img[n] = it["colour_img"][c]
        chart = next((im for it in srcs for im in it["images"] if im["chart"] and im.get("key")), None)
        live = [r for r in rows if r[-1]]
        first = srcs[0]
        prices = [r[2] for r in (live or rows)]
        colours = [n for n in names if any(r[0] == n and r[-1] for r in rows)] or names
        bullets = [f"Gioberti style {cfg['code']}"] + [b for b in first["bullets"] if not re.match(r"(style|sizes?)\b", b, re.I)]
        out.append(dict(first, handle=cfg["handle"], name=cfg["name"], code=cfg["code"], soldout=not live,
                        options=[dict(name="Color", values=names), dict(name="Size", values=sizes)], variants=rows,
                        colours=colours, all_colours=names, families=families(names), colour_img=colour_img,
                        price=min(prices), price_max=max(prices), bullets=bullets, images=images + ([chart] if chart else []),
                        supplier_url=" ".join(i["supplier_url"] for i in srcs),
                        merged_from=[i["handle"] for i in srcs] + cfg.get("retired", [])))
        used.update(i["handle"] for i in srcs)
    return [i for i in items if i["handle"] not in used] + out


ITEMS = curate(ITEMS)
HIDDEN_PAGES = {i["handle"]: category_of(i["handle"], i["ptype"], i["name"]) for i in ITEMS if i["handle"] in HIDDEN}   # left off on purpose -> their category
HIDDEN_PAGES.update({i["handle"]: None for i in ITEMS if category_of(i["handle"], i["ptype"], i["name"]) in HIDDEN_CATS})   # a whole category off -> its department
ITEMS = [i for i in ITEMS if i["handle"] not in HIDDEN_PAGES]


# ---------------------------------------------------------------- photo flow (owner, 2026-10-22: "reorganize the pictures to flow better by color and model")
# Colours are listed so similar shades sit together (dropdown and gallery), and the gallery runs colour by colour: each colour's own photo, then the
# model / detail shots of that colour. Gioberti leaves most model shots untagged; each is matched to the colour shot it looks most like (garment
# colours in the middle of the photo), and kept at the end when no colour is a clear match.
SHADE_ORDER = ["Black", "Charcoal", "Grey", "Silver", "White", "Beige", "Brown", "Gold", "Yellow", "Orange", "Red", "Burgundy", "Pink", "Purple",
               "Green", "Teal", "Blue", "Navy", "Other"]


def _shade(colour):
    first = re.split(r"\s*/\s*|\s+w/\s+", _plain(re.sub(r"\s*\(\d+\)$", "", colour)))[0]
    fam = families([first])[0]
    return SHADE_ORDER.index(fam) if fam in SHADE_ORDER else len(SHADE_ORDER)


_SIG = {}


def _signature(key):
    """Colour histogram of the garment area (middle of the photo, white background left out)."""
    if key not in _SIG:
        im = Image.open(os.path.join(ROOT, ASSET, key + "-t.webp")).convert("RGB")
        w, h = im.size
        px = np.asarray(im.crop((int(w * .25), int(h * .3), int(w * .75), int(h * .75)))).reshape(-1, 3).astype(int)
        px = px[px.min(axis=1) < 225]
        q = px // 43                                                       # 6 levels per channel: tells dark plaids apart
        hist = np.bincount(q[:, 0] * 36 + q[:, 1] * 6 + q[:, 2], minlength=216).astype(float)
        _SIG[key] = list(hist / (hist.sum() or 1))
    return _SIG[key]


def flow(it):
    colour_opt = it["options"][0] if it["all_colours"] else None
    if colour_opt:
        keep_solids_last = any("(" in c for c in it["all_colours"])        # curated plaids first, then the solids
        order = sorted(colour_opt["values"], key=lambda c: ((keep_solids_last and "(" not in c), _shade(c), colour_opt["values"].index(c)))
        colour_opt["values"] = order
        it["all_colours"] = [c for c in order if c in it["all_colours"]]
        it["colours"] = [c for c in order if c in it["colours"]]
    shots = [im for im in it["images"] if not im["chart"] and im.get("key")]
    charts = [im for im in it["images"] if im["chart"]]
    tagged = [im for im in shots if im.get("colours")]
    if not colour_opt or not tagged:
        return
    placed = {c: [] for c in it["all_colours"]}
    loose = []
    for im in shots:
        if im.get("colours"):
            placed.setdefault(im["colours"][0], []).append(im)
            continue
        sig = _signature(im["key"])
        dist = sorted((sum(abs(a - b) for a, b in zip(sig, _signature(t["key"]))), t["colours"][0]) for t in tagged)
        if dist and (len(dist) == 1 or dist[0][0] < 0.85 * dist[1][0]) and dist[0][0] < 1.3:
            placed.setdefault(dist[0][1], []).append(dict(im, colours=[dist[0][1]], matched=True))
        else:
            loose.append(im)
    for c in placed:                                                       # each colour: its own photo first, then its model / detail shots
        placed[c].sort(key=lambda im: bool(im.get("matched")))
    ordered = [im for c in it["all_colours"] for im in placed.get(c, [])] + [im for c, ims in placed.items() if c not in it["all_colours"] for im in ims]
    it["images"] = ordered + loose + charts


for _it in ITEMS:
    flow(_it)


for _it in ITEMS:
    _it["cat"] = category_of(_it["handle"], _it["ptype"], _it["name"])
    _it["file"] = f"gioberti-{_it['handle']}.html"
    _it["dept"] = dept_of(_it["handle"], _it["cat"])
UNFILED = [i for i in ITEMS if not i["cat"]]
ITEMS = [i for i in ITEMS if i["cat"]]
ITEMS.sort(key=lambda i: i["soldout"])                         # sold-out products last in every list (stable: supplier order otherwise)
BY_CAT = {}
for _it in ITEMS:
    BY_CAT.setdefault(_it["cat"], []).append(_it)
ACCESSORIES = {k: BY_CAT.get(k, []) for k in FORMAL_ACCESSORIES}       # also shown on bishop.html: men's in the main grid, boys' in their own section
# Kids collections that are not categories (a fit / an occasion), listed after the categories in the Kids Formal list (label, url)
FORMAL_EXISTING = {
    "men": [],
    "boys": [("Husky fit", "pawn-husky.html"), ("Ring bearer", "pawn-ring-bearer.html")],
}

# ---------------------------------------------------------------- other brands in the same categories (one page per category, every brand)
# Antonio Uomo: its cards on king.html (generated by gen_antonio.py), picked by their Style; they link to the Antonio Uomo product pages.
KING_STYLES = {"men-suits": ("Two-piece", "Three-piece"), "men-tuxedos": ("Tuxedo",), "men-blazers": ("Jacket",), "men-dress-pants": ("Pants",)}
# Magen Kids: every piece of these lines (tools/gen_pawn_pages.py) gets a product page here (magen-kids-<line>-<colour>.html) and a card in its category.
MAGEN_CATS = {"slim-fit": "boys-suits-blazers", "husky-suit": "boys-suits-blazers", "tuxedo": "boys-tuxedos", "husky-tuxedo": "boys-tuxedos",
              "suit-vest-set": "boys-suit-vests", "tuxedo-vest-set": "boys-suit-vests", "dress-pants": "boys-dress-pants", "husky-dress-pants": "boys-dress-pants"}
MAGEN_NAME = {"slim-fit": "Slim Fit Suit", "tuxedo": "Tuxedo", "suit-vest-set": "Suit Vest Set", "tuxedo-vest-set": "Tuxedo Vest Set",
              "husky-suit": "Husky Suit", "husky-tuxedo": "Husky Tuxedo", "dress-pants": "Dress Pants", "husky-dress-pants": "Husky Dress Pants"}
MAGEN = pw.BRAND
KID_SIZES = json.loads(pw.KID_OPTIONS)[0]["values"]


def king_cards(styles):
    """Antonio Uomo cards of the given Styles from king.html, tagged with brand / fit / availability so every filter on a mixed page works."""
    src = open(os.path.join(ROOT, "king.html"), encoding="utf-8").read()
    out = []
    for c in re.findall(r'[ \t]*<a class="product-card au-card"[^>]*>.*?</a>', src, re.S):
        st = re.search(r'data-f-style="([^"]*)"', c)
        if st and st.group(1) in styles:
            c = c.replace(' data-f-color=', ' data-f-brand="Antonio Uomo" data-f-fit="Regular" data-f-availability="In stock" data-f-color=', 1)
            out.append(dict(card=c, price=float(re.search(r'data-price="([\d.]+)"', c).group(1)), img=re.search(r'data-img="([^"]+)"', c).group(1)))
    return out


def magen_items():
    out = []
    for line, slug, name, cfg in pw.all_pieces():
        if line not in MAGEN_CATS:
            continue
        colour = htmllib.unescape(name)
        base = f"assets/img/pawn/{line}/{slug}"
        files = os.listdir(os.path.join(ROOT, base))
        shots = sorted(f for f in files if re.fullmatch(r"model-\d+\.jpg", f)) + sorted(f for f in files if re.fullmatch(r"plain-\d+\.jpg", f))
        pics = []
        for i, f in enumerate(shots, 1):
            w, h = Image.open(os.path.join(ROOT, base, f)).size
            pics.append(dict(src=f"{base}/{f}", thumb=f"{base}/thumb-{i}.jpg", w=w, h=h))
        out.append(dict(line=line, slug=slug, colour=colour, cfg=cfg, cat=MAGEN_CATS[line], file=f"magen-kids-{line}-{slug}.html",
                        name=f"{colour} {MAGEN_NAME[line]}", label=MAGEN_NAME[line], price=cfg["price"], fit=cfg.get("fit", "Regular"),
                        sizes=cfg.get("sizes") or KID_SIZES, code=cfg.get("code", ""), pics=pics, families=families([colour])))
    return out


MAGEN_ITEMS = magen_items()


def magen_card(m):
    pic = m["pics"][0]["src"]
    c = (f'            <a class="product-card au-card" href="{m["file"]}" data-id="pawn/{m["line"]}/{m["slug"]}" data-name="{esc(m["name"])}" data-tag="{esc(m["label"])}" '
         f'data-price="{m["price"]:g}" data-img="{pic}" data-f-color="{esc("|".join(m["families"]))}" data-f-brand="{MAGEN}" data-f-fit="{m["fit"]}" data-f-availability="In stock">\n'
         f'              <span class="au-card__img"><img src="{pic}" alt="{esc(m["name"])}" loading="lazy" width="480" height="720"></span>\n'
         f'              <div class="product-card__meta"><div><h4>{esc(m["name"])}</h4><span class="piece-tag">{esc(MAGEN)} &middot; {esc(m["label"])}</span></div><span class="product-card__price">{money(m["price"])}</span></div>\n'
         f'            </a>')
    return dict(price=m["price"], img=pic, card=c)


EXTERNAL = {}
for _k, _styles in KING_STYLES.items():
    EXTERNAL.setdefault(_k, []).extend(king_cards(_styles))
for _m in MAGEN_ITEMS:
    EXTERNAL.setdefault(_m["cat"], []).append(magen_card(_m))


def img(key, kind=""):
    return f"{ASSET}{key}{kind}.webp"


def photos(it):
    """Gallery photos: every photo except the size chart (sold-out colours too: they stay listed, marked sold out)."""
    return [im for im in it["images"] if not im["chart"] and im.get("key")]


def cover(it):
    """Card photo: the first in-stock colour's own photo, else the first photo."""
    key = next((it["colour_img"][c] for c in it["colours"] if c in it["colour_img"]), None)
    return key or (photos(it) or it["images"])[0]["key"]


def price_text(it):
    return money(it["price"]) if it["price"] == it["price_max"] else "From " + money(it["price"])


def cat_files(dept, group):
    return [k for k, v in CATS.items() if v[0] == dept and v[1] == group and (BY_CAT.get(k) or EXTERNAL.get(k))]


def card(it, with_cat=False):
    pic = img(cover(it), "-c")
    n = len(it["all_colours"])
    label = CATS[it["cat"]][2]
    fx = f' data-f-color="{esc("|".join(it["families"]))}" data-f-brand="{BRAND}" data-f-fit="{"Husky" if "husky" in it["name"].lower() else "Regular"}" data-f-availability="{"Sold out" if it["soldout"] else "In stock"}"' + (f' data-f-category="{esc(label)}"' if with_cat else "")
    badge = '<em class="gb-soldout">Sold out</em>' if it["soldout"] else ""
    return f'''            <a class="product-card au-card{" is-soldout" if it["soldout"] else ""}" href="{it["file"]}" data-id="gioberti/{it["handle"]}" data-name="{esc(it["name"])}" data-tag="{esc(label)}" data-price="{it["price"]:g}" data-img="{pic}"{fx}>
              <span class="au-card__img"><img src="{pic}" alt="{esc(it["name"])}" loading="lazy" width="480" height="640">{badge}</span>
              <div class="product-card__meta"><div><h4>{esc(it["name"])}</h4><span class="piece-tag">{esc(label)} &middot; {esc(it["code"])}{f" &middot; {n} colours" if n > 1 else ""}</span></div><span class="product-card__price">{"Sold out" if it["soldout"] else price_text(it)}</span></div>
            </a>'''


def pills(dept, group, active):
    d = DEPTS[dept]
    landing = d[group]
    links = [(landing, f"All {GROUP_LABEL[group].lower()}")]                     # (href, label)
    links += [(f"{k}.html", CATS[k][2]) for k in cat_files(dept, group)]
    if group == "formal":
        links += [(u, l) for l, u in FORMAL_EXISTING[dept]]
    if group == "formal" and dept == "men":
        links.append(("bishop.html", "All accessories"))                          # the Accessories department (bow ties, cufflinks…)
    on =' class="is-on" aria-current="page"'
    return f'<nav class="au-cats" aria-label="{GROUP_LABEL[group]} categories"><div class="container">' + "".join(
        f'<a href="{h}"{on if h == active else ""}>{esc(l)}</a>' for h, l in links) + "</div></nav>"


def dept_crumbs(dept, group, *more):
    d = DEPTS[dept]
    return [("Home", "index.html"), d["crumb"], (GROUP_LABEL[group], d[group]), *more]


SHOP_JS = '<script src="js/shop.js?v=7"></script>'


def build_category(key):
    """One page per category with every brand: Gioberti in stock, then the other brands (Antonio Uomo / Magen Kids), then sold-out pieces."""
    dept, group, label, blurb = CATS[key]
    d = DEPTS[dept]
    its, ext = BY_CAT.get(key, []), EXTERNAL.get(key, [])
    cards = [card(i) for i in its if not i["soldout"]] + [e["card"] for e in ext] + [card(i) for i in its if i["soldout"]]
    facets = [{"key": "style", "label": "Style"}, {"key": "brand", "label": "Brand"}, {"key": "fit", "label": "Fit"}, {"key": "color", "label": "Colour", "swatch": True},
              {"key": "pattern", "label": "Pattern"}, {"key": "availability", "label": "Availability"}]          # a filter with one value hides itself
    lo = min([i["price"] for i in its] + [e["price"] for e in ext])
    first = [img(cover(i), "-c") for i in its if not i["soldout"]] + [e["img"] for e in ext] + [img(cover(i), "-c") for i in its]
    title = f"{d['poss']} {label}"
    head = page_head(crumbs(*dept_crumbs(dept, group, (label, f"{key}.html"))), esc(title), f"{esc(blurb)} {len(cards)} pieces from {money(lo)}.")
    body = f"{head}\n{pills(dept, group, key + '.html')}\n{shop_block(chr(10).join(cards), facets, 'category', count_noun='pieces', review_facets=[])}"
    write(f"{key}.html", shell(f"{title} — {GROUP_LABEL[group]} | Checkmatela", f"{title} at Checkmatela: {len(cards)} pieces from {money(lo)}. {blurb}",
                               body, glyph=d["glyph"], extra_js=SHOP_JS))
    return dict(key=key, label=label, n=len(cards), lo=lo, img=first[0])


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
    tiles += [style_card(f"{b['key']}.html", b["label"], f"{b['n']} pieces from {money(b['lo'])}.", f"Shop {b['label'].lower()}", photo=b["img"]) for b in built if CATS[b["key"]][0] == dept and CATS[b["key"]][1] == group]
    if group == "formal":
        tiles += [style_card(u, l, f"Browse the full {l.lower()} collection.", f"Shop {l.lower()}", glyph=d["glyph"]) for l, u in FORMAL_EXISTING[dept]]
        if dept == "men":
            tiles.append(style_card("bishop.html", "All accessories", "Bow ties, pocket squares, cufflinks and more.", "Shop accessories", glyph=d["glyph"]))
        lead = f"Everything for the formal occasion: suits, tuxedos, blazers, vests, dress shirts and dress pants for {who}."
        h2 = "Dressed for the occasion."
    else:
        lead = f"Everyday and off-duty pieces for {who}: shirts, sweaters, jackets, activewear and more, for when the dress code is relaxed."
        h2 = "Relaxed, not careless."
    title = f"{d['poss']} {GROUP_LABEL[group]}"
    head = page_head(crumbs(*dept_crumbs(dept, group)), esc(title), esc(lead))
    grid = ""
    if group == "nsf":
        its = [i for k in cat_files(dept, "nsf") for i in BY_CAT[k]]
        grid = shop_block("\n".join(card(i, with_cat=True) for i in its), [{"key": "category", "label": "Category"}, {"key": "color", "label": "Colour", "swatch": True}, {"key": "availability", "label": "Availability"}],
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
    thumbs = "".join(f'<button type="button" class="pdp-thumb{" is-active" if im is first else ""}" data-src="{img(im["key"])}" data-w="{im["w"]}" data-h="{im["h"]}"{f' data-colour="{esc(im["colours"][0])}"' if len(im.get("colours") or []) == 1 else ""}{f' data-sleeve="{im["sleeve"]}"' if im.get("sleeve") else ""} aria-label="Show photo {n} of {len(ims)}"><img src="{img(im["key"], "-t")}" alt="" loading="lazy" width="72" height="72"></button>'
                     for n, im in enumerate(ims, 1))
    main = f'<img id="pdpMain" src="{img(first["key"])}" alt="{esc(it["name"])}" width="900" height="{round(900 * first["h"] / first["w"])}" fetchpriority="high">'
    return f'<div class="pdp-gallery"><div class="pdp-main" id="pdpFrame" style="--r:{first["w"] / first["h"]:.4f}">{main}</div>{f"<div class=pdp-thumbs>{thumbs}</div>" if len(ims) > 1 else ""}</div>'.replace("<div class=pdp-thumbs>", '<div class="pdp-thumbs">')


def option_selects(it):
    """One dropdown per option (colour first) listing every value the supplier offers; values with no in-stock variant say "sold out"
    (js/product.js keeps that up to date as the other option changes). A colour option carries its own photo."""
    dims = {im["key"]: im for im in it["images"] if im.get("key")}
    out = []
    for oi, o in enumerate(it["options"]):
        attrs = {}
        if oi == 0 and it["all_colours"]:
            for v in o["values"]:
                if v in it["colour_img"] and it["colour_img"][v] in dims:
                    im = dims[it["colour_img"][v]]
                    attrs[v] = f' data-img="{img(im["key"])}" data-w="{im["w"]}" data-h="{im["h"]}" data-thumb="{img(im["key"], "-t")}"'
        out_vals = [v for v in o["values"] if not any(r[oi] == v and r[-1] for r in it["variants"])]
        key = re.sub(r"[^a-z]", "", o["name"].lower()) or "option"
        shown = next((c for c in it["colours"] if it["colour_img"].get(c) == cover(it)), None) if oi == 0 and it["all_colours"] else None   # the colour in the main photo
        out.append(select_opt(key, o["name"], o["values"], default=shown, attrs=attrs, soldout=out_vals, show_chosen=oi == 0 and bool(it["all_colours"])))
    return "\n        ".join(out)


CHART_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M3 15 15 3l6 6L9 21z"/><path d="M7 11l2 2M10 8l2 2M13 5l2 2M5 13l1 1"/></svg>'


def build_product(it):
    cat = it["cat"]
    dept, group, label, _ = CATS[cat]
    parts = dept_crumbs(dept, group, (label, f"{cat}.html"), (it["name"], it["file"]))
    eyebrow, more_href = f"{BRAND} &middot; {DEPTS[dept]['label']} &middot; {GROUP_LABEL[group]}", f"{cat}.html"
    related = [i for i in BY_CAT[cat] if i is not it][:4]
    charts = [im for im in it["images"] if im["chart"] and im.get("key")]
    chart = charts[0] if charts else None
    chart_btn = f'<button type="button" class="pdp-chart-btn" data-open-chart aria-haspopup="dialog">{CHART_ICON}Size chart</button>' if chart else ""
    chart_dialog = (f'<dialog class="shop-dialog au-chart" id="sizeChart" aria-labelledby="gbChartTitle"><button type="button" class="shop-dialog__x" aria-label="Close size chart">×</button>'
                    f'<div class="au-chart__body"><h2 class="au-chart__title" id="gbChartTitle">{esc(it["name"])} size chart</h2>{"".join((f'<h3 class="au-chart__sub">{esc(ch["label"])}</h3>' if ch.get("label") else "") + f'<img class="gb-chart" src="{img(ch["key"], "-z")}" alt="{esc(it["name"])} size chart" loading="lazy" width="{min(1400, ch["w"])}" height="{round(min(1400, ch["w"]) * ch["h"] / ch["w"])}">' for ch in charts)}'
                    f'<p class="au-size__note">Measurements from {BRAND}, for this product. Not sure between two sizes? <a class="link" href="book-a-fitting.html?look={esc(it["name"].replace(" ", "%20"))}">Ask us about fit</a>.</p></div></dialog>') if chart else ""
    n = len(it["all_colours"])
    lede = f"{it['name']} by {BRAND}" + (f", in {n} colours." if n > 1 else ".") + (
        " This piece is currently sold out; ask us about restocks." if it["soldout"] else " Choose your options, then add it to your preview bag or ask us about fit.")
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
        <p class="pdp-price">{price_text(it)}{'<span class="gb-soldout gb-soldout--inline">Sold out</span>' if it["soldout"] else ""}</p>
        <p class="pdp-lede">{esc(lede)}</p>
        {option_selects(it)}
        {chart_btn}
        <p class="pdp-msg" role="status"></p>
        <div class="pdp-cta">{'<button type="button" class="btn pdp-add" disabled>Sold out</button>' if it["soldout"] else '<button type="button" class="btn pdp-add">Add to preview bag</button>'}<a class="btn dark-ghost" href="book-a-fitting.html?look={esc(it["name"].replace(" ", "%20"))}">Ask about fit</a></div>
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
                            body, glyph=glyph, extra_js='<script src="js/product.js?v=9"></script>'))


def build_magen_product(m):
    """A Magen Kids piece (photos from assets/img/pawn/<line>/<colour>/) as a product page like every other brand's: gallery, size dropdown, details."""
    cfg, cat = m["cfg"], m["cat"]
    dept, group, label, _ = CATS[cat]
    parts = dept_crumbs(dept, group, (label, f"{cat}.html"), (m["name"], m["file"]))
    pics = m["pics"]
    thumbs = "".join(f'<button type="button" class="pdp-thumb{" is-active" if n == 1 else ""}" data-src="{p["src"]}" data-w="{p["w"]}" data-h="{p["h"]}" aria-label="Show photo {n} of {len(pics)}"><img src="{p["thumb"]}" alt="" loading="lazy" width="72" height="72"></button>'
                     for n, p in enumerate(pics, 1))
    first = pics[0]
    gal = (f'<div class="pdp-gallery"><div class="pdp-main" id="pdpFrame" style="--r:{first["w"] / first["h"]:.4f}"><img id="pdpMain" src="{first["src"]}" alt="{esc(m["name"])}" width="900" height="{round(900 * first["h"] / first["w"])}" fetchpriority="high"></div>'
           + (f'<div class="pdp-thumbs">{thumbs}</div>' if len(pics) > 1 else "") + '</div>')
    inc = pw.COMPARE.get(m["line"])
    bullets = []
    if inc:
        bullets.append("Includes: " + ", ".join(x for x, on in (("jacket", inc["jacket"]), ("vest", inc["vest"]), ("trousers", inc["trousers"]), ("shirt", inc["shirt"])) if on) + f", {inc['tie'].lower()}")
        bullets.append(f"Best for: {inc['best']}")
    if m["fit"] == "Husky":
        bullets.append(f"Husky fit: cut roomier, sizes {m['sizes'][0]} to {m['sizes'][-1]} (preview range, confirm with us)")
    else:
        bullets.append(f"Sizes {m['sizes'][0]} to {m['sizes'][-1]}")
    lede = htmllib.unescape(cfg.get("intro", "")) or f"{m['name']} by {MAGEN}, for weddings, church, school events and family portraits."
    details = "<ul class=\"pdp-list\">" + "".join(f"<li>{esc(b)}</li>" for b in bullets) + "</ul>"
    sib = [x for x in MAGEN_ITEMS if x["line"] == m["line"] and x is not m]
    rel = ""
    if sib:
        rel = f'''<section class="section pdp-related">
  <div class="container">
    <div class="section-head"><span class="eyebrow">More colours</span><h2>{esc(m["label"])}</h2></div>
    <div class="product-grid">
{chr(10).join(magen_card(x)["card"] for x in sib[:4])}
    </div>
    <p style="text-align:center;margin-top:28px"><a class="btn dark-ghost" href="{cat}.html">See all {esc(label.lower())}</a></p>
  </div>
</section>'''
    code = f"Style {esc(m['code'])} &middot; " if m["code"] else ""
    body = f'''<main class="pdp" id="pdp" data-id="pawn/{m["line"]}/{m["slug"]}" data-name="{esc(m["name"])}" data-tag="{esc(MAGEN)} · {esc(m["label"])}" data-price="{m["price"]:g}" data-img="{first["src"]}">
  <div class="container">
    {crumbs(*parts).replace('class="crumbs"', 'class="crumbs crumbs--light"')}
    <div class="pdp__grid">
      {gal}
      <div class="pdp-info">
        <span class="eyebrow">{esc(MAGEN)} &middot; Kids &middot; Formal</span>
        <h1>{esc(m["name"])}</h1>
        <p class="pdp-code">{code}{esc(label)}</p>
        <p class="pdp-price">{money(m["price"])}</p>
        <p class="pdp-lede">{esc(lede)}</p>
        {colour_row(m["colour"], m["pics"][0]["thumb"])}
        {select_opt("size", "Size", m["sizes"])}
        <a class="pdp-chart-btn" href="size-guide.html">{CHART_ICON}Kids' size guide</a>
        <p class="pdp-msg" role="status"></p>
        <div class="pdp-cta"><button type="button" class="btn pdp-add">Add to preview bag</button><a class="btn dark-ghost" href="book-a-fitting.html?look={esc(m["name"].replace(" ", "%20"))}">Ask about fit</a></div>
        <p class="pdp-assure"><a href="shipping-returns.html">Free exchanges and easy returns</a></p>
        <p class="pdp-fine">Preview only: prices and availability are not confirmed, and checkout is not connected.</p>
        <div class="pdp-accs">
          {acc("Details", details, True)}
        </div>
      </div>
    </div>
  </div>
</main>

{rel}'''
    write(m["file"], shell(f"{m['name']} — {MAGEN} | Checkmatela", f"{m['name']} by {MAGEN}, {money(m['price'])}. Sizes {m['sizes'][0]} to {m['sizes'][-1]}, photos and details at Checkmatela.",
                           body, glyph="glyph-pawn", extra_js='<script src="js/product.js?v=9"></script>'))


def stamp_bishop():
    path = os.path.join(ROOT, "bishop.html")
    """Men's cummerbund / suspender sets join the main Accessories grid; boys' sets get their own "For boys" section under it, so the two never mix."""
    src = open(path, encoding="utf-8").read()
    if "<!-- GIOBERTI:START -->" not in src:
        src = src.replace('<div class="product-grid" data-reveal-group>', '<div class="product-grid" data-reveal-group>\n<!-- GIOBERTI:START -->\n<!-- GIOBERTI:END -->', 1)
    src = replace_between(src, "<!-- GIOBERTI:START -->", "<!-- GIOBERTI:END -->", "\n".join(card(i) for i in ACCESSORIES["men-formal-accessories"]))
    boys = ACCESSORIES["boys-formal-accessories"]
    section = f'''<section class="section" id="boys" style="padding-top:0">
  <div class="container">
    <div class="section-head"><span class="eyebrow">For boys</span><h2>Boys' formal accessories</h2><p>Cummerbund and suspender sets sized for boys. <a class="link" href="boys-formal-accessories.html">Shop all boys' formal accessories</a></p></div>
    <div class="product-grid">
{chr(10).join(card(i) for i in boys)}
    </div>
  </div>
</section>''' if boys else ""
    if "<!-- GIOBERTI-BOYS:START -->" not in src:
        i = src.index("</section>", src.index('<div class="product-grid" data-reveal-group>')) + len("</section>")
        src = src[:i] + "\n\n<!-- GIOBERTI-BOYS:START -->\n<!-- GIOBERTI-BOYS:END -->" + src[i:]
    src = replace_between(src, "<!-- GIOBERTI-BOYS:START -->", "<!-- GIOBERTI-BOYS:END -->", section)
    n = len(re.findall(r'<a class="product-card[ "]', src))
    src = re.sub(r'<span class="filter-bar__count">\d+ pieces in this collection</span>', f'<span class="filter-bar__count">{n} pieces in this collection</span>', src)
    open(path, "w", encoding="utf-8").write(src)


def stamp_dresscode_bar(page, dept):
    """A Formal / Not So Formal category bar right under the department intro (king.html, pawn.html)."""
    d = DEPTS[dept]
    links = [f'<a href="{d["formal"]}"><b>Formal</b></a>'] + [f'<a href="{k}.html">{esc(CATS[k][2])}</a>' for k in cat_files(dept, "formal")]
    links += [f'<a href="{u}">{esc(l)}</a>' for l, u in FORMAL_EXISTING[dept]]
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
        men_acc = it["cat"] == "men-formal-accessories"                   # men's cummerbund / suspender sets also belong to the Accessories department
        k, d = ("Bishop", "Accessories") if men_acc else (DEPTS[it["dept"]]["sub"], DEPTS[it["dept"]]["label"] if it["dept"] == "men" else "Kids")
        label = it["name"] if men_acc else CATS[it["cat"]][2]
        out.append(dict(k=k, d=d + " " + " ".join(it["all_colours"]), t=it["name"], s=f"{BRAND} · {label}" + (" · Sold out" if it["soldout"] else ""), u=it["file"], p=it["price"], i=img(cover(it), "-c"), f={"color": it["families"][0]}))
    return out


def search_pages():
    pages = []
    for dept, d in DEPTS.items():
        kw = "men mens" if dept == "men" else "kids boys"
        pages.append((f"{d['poss']} Formal", d["formal"], d["crumb"][0], f"formal suits tuxedos blazers vests dress shirts dress pants {kw}"))
        pages.append((f"{d['poss']} Not So Formal", d["nsf"], d["crumb"][0], f"not so formal casual everyday sweaters hoodies jackets polos activewear sleepwear {kw}"))
    for k, (dept, group, label, _) in CATS.items():
        if BY_CAT.get(k) or EXTERNAL.get(k):
            pages.append((f"{DEPTS[dept]['poss']} {label}", f"{k}.html", DEPTS[dept]["crumb"][0], f"{label} {GROUP_LABEL[group]} {'men mens' if dept == 'men' else 'kids boys'} gioberti".lower()))
    return pages


def redirect_merged():
    """Permanent redirects in vercel.json from the pages of listings that were combined (CURATED) to the combined page."""
    path = os.path.join(ROOT, "vercel.json")
    cfg = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    keep = [r for r in cfg.get("redirects", []) if not r["source"].startswith("/gioberti-") and r["source"] not in {f"/{c}.html" for c in HIDDEN_CATS}]
    new = [{"source": f"/gioberti-{h}.html", "destination": f"/{it['file']}", "permanent": True} for it in ITEMS for h in it.get("merged_from", [])]
    new += [{"source": f"/gioberti-{h}.html", "destination": f"/{cat}.html" if cat else "/men-not-so-formal.html", "permanent": True} for h, cat in HIDDEN_PAGES.items()]
    new += [{"source": f"/{c}.html", "destination": f"/{DEPTS[CATS[c][0]][CATS[c][1]]}", "permanent": True} for c in sorted(HIDDEN_CATS)]       # removed category pages
    cfg["redirects"] = keep + new
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(cfg, indent=2) + "\n")


def main():
    if UNFILED:
        print("WARNING: no category for", ", ".join(f"{i['handle']} ({i['ptype']})" for i in UNFILED), "- add the type to TYPE_MAP")
    built = [build_category(k) for k in CATS if BY_CAT.get(k) or EXTERNAL.get(k)]
    for dept in DEPTS:
        for group in ("formal", "nsf"):
            build_landing(dept, group, built)
    for it in ITEMS:
        build_product(it)
    for m in MAGEN_ITEMS:
        build_magen_product(m)
    stamp_bishop()
    stamp_dresscode_bar("king.html", "men")
    stamp_dresscode_bar("pawn.html", "boys")
    wanted = {i["file"] for i in ITEMS} | {m["file"] for m in MAGEN_ITEMS} | {f"{b['key']}.html" for b in built} | {d[g] for d in DEPTS.values() for g in ("formal", "nsf")}
    for f in os.listdir(ROOT):                                   # drop pages of products Gioberti no longer sells and of categories that were merged away
        if re.fullmatch(r"(gioberti|men|boys|magen-kids)-[a-z0-9-]+\.html", f) and f not in wanted:
            os.remove(os.path.join(ROOT, f))
            print("removed", f)
    redirect_merged()
    print("gioberti:", len(built), "category pages, 4 landing pages,", len(ITEMS), "Gioberti +", len(MAGEN_ITEMS), "Magen Kids product pages,", sum(map(len, ACCESSORIES.values())), "on bishop.html")
    import gen_nav
    gen_nav.main()


if __name__ == "__main__":
    main()
