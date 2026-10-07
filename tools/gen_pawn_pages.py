"""Generates the four Pawn category pages (pawn-slim-fit / suit-vest-set / tuxedo / tuxedo-vest-set .html).

Run from anywhere:  python3 tools/gen_pawn_pages.py
Reads the processed images under assets/img/pawn/ (see process_pawn_images.py and make_hero_cutouts.py).
"""
import os, glob, html
from PIL import Image
from shoplib import shop_block, replace_between, swatch_hex, tone_of, esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_VERSION = "72"
FAVICON = '<link rel="icon" type="image/svg+xml" href="brand/svg/favicon.svg?v=2">'

GLYPH_PAWN = '''    <symbol id="glyph-pawn" viewBox="0 0 100 130">
      <circle fill="currentColor" cx="50" cy="30" r="13"/>
      <path fill="currentColor" d="M39 46 C39 40 61 40 61 46 L55 60 H45 Z"/>
      <path fill="currentColor" d="M43 60 H57 L64 100 H36 Z"/>
      <path fill="currentColor" d="M28 100 H72 L69 108 H31 Z"/>
      <path fill="currentColor" d="M22 108 H78 L74 128 H26 Z"/>
    </symbol>'''

GLYPH_KING = '''    <symbol id="glyph-king" viewBox="0 0 100 130">
      <path fill="currentColor" d="M47 4 H53 V13 H62 V19 H53 V28 H47 V19 H38 V13 H47 Z"/>
      <circle fill="currentColor" cx="50" cy="35" r="6.5"/>
      <path fill="currentColor" d="M37 43 C37 37 63 37 63 43 C66 49 65 55 60 59 C67 63 69 69 67 75 L33 75 C31 69 33 63 40 59 C35 55 34 49 37 43 Z"/>
      <path fill="currentColor" d="M42 75 H58 L64 100 H36 Z"/>
      <path fill="currentColor" d="M28 100 H72 L69 108 H31 Z"/>
      <path fill="currentColor" d="M22 108 H78 L74 128 H26 Z"/>
    </symbol>'''

HEADER = '''<header class="site-header" id="siteHeader">
  <div class="hdr-left">
    <a class="McButton" data="hamburger-menu" role="button" tabindex="0" aria-label="Open menu" aria-expanded="false" aria-controls="siteMenu"><b></b><b></b><b></b></a>
    <span class="hdr-menu-label" aria-hidden="true">Menu</span>
    <nav class="main-nav" id="mainNav" aria-label="Main">
      <a href="king.html" data-mega="king">Men</a>
      <a href="queen.html" data-mega="queen">Women</a>
      <a href="pawn.html" data-mega="pawn">Kids</a>
      <a href="bishop.html" data-mega="bishop">Accessories</a>
      <a href="rook.html" data-mega="rook">Shoes</a>
      <a href="find-your-look.html" data-mega="discover">Discover</a>
    </nav>
  </div>
  <a href="index.html" class="brand" aria-label="Checkmatela home"><img src="brand/svg/compact-horizontal.svg?v=2" alt="" width="235" height="45"></a>
  <div class="header-actions">
    <a class="hdr-cta" href="find-your-look.html">Find your look</a>
    <button class="icon-btn search-ic" aria-label="Search" aria-haspopup="dialog"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg></button>
    <button class="icon-btn" aria-label="Bag"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M6 8h12l-1 13H7L6 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg></button>
  </div>
</header>'''

FOOTER = '''<footer class="site-footer">
  <div class="container footer-top">
    <div class="footer-brand">
      <a href="index.html" class="brand" aria-label="Checkmatela home"><img src="brand/svg/compact-horizontal-reverse.svg?v=2" alt="" width="235" height="45"></a>
      <p>Formal wear for weddings, celebrations and the moments in between. Find a look that fits the occasion, then plan the details with confidence.</p>
      <div class="footer-social"><a href="mailto:suit.shop.dtla@gmail.com?subject=Checkmatela%20event%20enquiry" aria-label="Email Checkmatela about your event"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="m3 7 9 7 9-7"/></svg></a></div>
    </div>
    <div class="footer-col"><h5>The Board</h5><ul>
      <li><a href="king.html">King — Men</a></li>
      <li><a href="queen.html">Queen — Women</a></li>
      <li><a href="pawn.html">Pawn — Kids</a></li>
      <li><a href="bishop.html">Bishop — Accessories</a></li>
      <li><a href="rook.html">Rook — Shoes</a></li>
    </ul></div>
    <div class="footer-col"><h5>Company</h5><ul>
      <li><a href="our-story.html">Our Story</a></li><li><a href="master-tailors.html">Master Tailors</a></li><li><a href="sustainability.html">Sustainability</a></li><li><a href="press.html">Press</a></li>
    </ul></div>
    <div class="footer-col"><h5>Service</h5><ul>
      <li><a href="find-your-look.html">Find Your Look</a></li><li><a href="book-a-fitting.html">Ask About Fit</a></li><li><a href="size-guide.html">Size Guide</a></li><li><a href="alterations.html">Alterations</a></li><li><a href="shipping-returns.html">Shipping &amp; Returns</a></li>
    </ul></div>
    <div class="footer-col"><h5>Contact</h5><ul>
      <li><a href="mailto:suit.shop.dtla@gmail.com">suit.shop.dtla@gmail.com</a></li>
      <li><a href="tel:+13108906991">+1 (310) 890-6991</a></li>
      <li>Los Angeles</li>
    </ul></div>
  </div>
  <div class="checker-strip"></div>
  <div class="container footer-bottom">
    <span>© 2026 Checkmatela. All moves reserved.</span>
    <div class="legal"><a href="shipping-returns.html">Service status</a><a href="mailto:suit.shop.dtla@gmail.com">Contact</a></div>
  </div>
</footer>

<script src="js/nav.js?v=15"></script>
<script src="js/main.js"></script>
<script src="js/cart.js?v=4"></script>
</body>
</html>'''

ANNOUNCE = '''<div class="announce">
  <div class="announce__inner">
    <div class="announce__msgs">
      <a href="find-your-look.html" style="--n:0">Dressing for an event? Start with your occasion</a>
      <a href="size-guide.html" style="--n:1">Find your fit before you choose a size</a>
      <a href="shipping-returns.html" style="--n:2">Have a date in mind? Ask about timing</a>
      <a href="king.html" style="--n:3">Bring 3+ groomsmen and save up to 15% together</a>
    </div>
    <div class="announce__links">
      <a href="tel:+13108906991">+1 (310) 890-6991</a>
      <a href="size-guide.html">Size Guide</a>
      <a href="book-a-fitting.html">Ask About Fit</a>
    </div>
  </div>
</div>'''

MODEL_ALTS = {1: "front view on model", 2: "angled pose on model", 3: "back view on model", 4: "trouser detail on model"}
PLAIN_ALTS = {1: "product only, front", 2: "product only, flat detail"}

LINES = {
    "suit-vest-set": dict(
        file="pawn-suit-vest-set.html", label="Suit Vest Set", price=115,
        title="Suit Vest Set — Pawn Kids | Checkmatela",
        meta="Checkmatela Pawn collection — Suit Vest Set for kids, in Black, Indigo, Light Gray and Navy.",
        intro="An easy dressed-up option for warm-weather weddings, family photos and school celebrations. Explore four colorways and compare the details before choosing a size.",
        colors=[("black", "Black"), ("indigo", "Indigo"), ("light-gray", "Light Gray"), ("navy", "Navy")],
        hero=["black", "indigo", "navy"],
    ),
    "tuxedo-vest-set": dict(
        file="pawn-tuxedo-vest-set.html", label="Tuxedo Vest Set", price=125,
        title="Tuxedo Vest Set — Pawn Kids | Checkmatela",
        meta="Checkmatela Pawn collection — Tuxedo Vest Set for kids, in Black, Burgundy, Light Gray and Light Navy.",
        intro="A polished vest look for formal celebrations when a full jacket is more than the moment needs. Compare four colorways and check measurements before the event.",
        colors=[("black", "Black"), ("burgundy", "Burgundy"), ("light-gray", "Light Gray"), ("light-navy", "Light Navy")],
        hero=["black", "burgundy", "light-navy"],
    ),
    "slim-fit": dict(
        file="pawn-slim-fit.html", label="Slim Fit", price=145,
        title="Slim Fit — Pawn Kids | Checkmatela",
        meta="Checkmatela Pawn collection — Slim Fit suits for kids in fourteen colorways.",
        intro="A modern suit look for weddings, school events and family portraits. Browse fourteen colorways, then use the fit guide to plan ahead.",
        colors=[("black", "Black"), ("navy", "Navy"), ("charcoal", "Charcoal"), ("light-gray", "Light Gray"),
                ("medium-gray", "Medium Gray"), ("white", "White"), ("beige-khaki", "Beige Khaki"),
                ("khaki", "Khaki"), ("light-navy", "Light Navy"), ("royal-blue", "Royal Blue"),
                ("sky-blue", "Sky Blue"), ("indigo-blue", "Indigo Blue"), ("hunter-green", "Hunter Green"),
                ("burgundy", "Burgundy")],
        hero=["navy", "burgundy", "hunter-green"],
    ),
    "tuxedo": dict(
        file="pawn-tuxedo.html", label="Tuxedo", price=159,
        title="Tuxedo — Pawn Kids | Checkmatela",
        meta="Checkmatela Pawn collection — shawl-lapel tuxedos for kids in twelve colorways.",
        intro="For black-tie weddings, prom and milestone celebrations. See the shawl-lapel look in twelve colorways and compare measurements before choosing.",
        colors=[("full-black", "Full Black"), ("white-black", "White &amp; Black"), ("full-white", "Full White"),
                ("charcoal", "Charcoal"), ("shiny-charcoal", "Shiny Charcoal"), ("gray", "Gray"),
                ("navy", "Navy"), ("royal-blue", "Royal Blue"), ("red", "Red"),
                ("burgundy", "Burgundy"), ("hunter-green", "Hunter Green"), ("khaki", "Khaki")],
        hero=["full-black", "red", "royal-blue"],
    ),
}
KID_OPTIONS = '[{"key": "size", "label": "Size", "values": ["2T", "4", "6", "8", "10", "12", "14", "16"], "required": true}]'
ORDER = ["slim-fit", "suit-vest-set", "tuxedo", "tuxedo-vest-set"]

# Pawn pages without product photography yet are placeholder pages generated by gen_info_pages.py (PAGES["pawn-husky"]).
# Everything on pawn.html's "Shop by Style" row and every "Complete the set" button list comes from here, in this order:
# add a page to this list (and create the page) and it appears on the Pawn landing page and in the menus.
PLACEHOLDER_PAGES = [dict(file="pawn-husky.html", label="Husky Fit", id="style-husky", text="Roomier suits, tuxedos and dress pants for husky boys in larger sizes. Coming soon.")]
LANDING = [
    dict(file=LINES_FILE, label=LABEL, id=ID, img=IMG, alt=ALT, text=TEXT)
    for LINES_FILE, LABEL, ID, IMG, ALT, TEXT in [
        ("pawn-slim-fit.html", "Slim Fit", "style-slimfit", "assets/img/pawn/slim-fit/navy/model-1.jpg", "Child model wearing the Checkmatela Slim Fit suit", "A modern suit look for weddings, school events and family portraits — 14 colorways."),
        ("pawn-suit-vest-set.html", "Suit Vest Set", "style-vestset", "assets/img/pawn/suit-vest-set/black/model-1.jpg", "Child model wearing the Checkmatela Suit Vest Set", "Jacket-free and effortless — shirt, vest and trouser set in four colorways."),
        ("pawn-tuxedo.html", "Tuxedo", "style-tuxedo", "assets/img/pawn/tuxedo/white-black/model-1.jpg", "Child model wearing the Checkmatela Tuxedo", "Black-tie formality, sized for the next generation's biggest nights — 12 colorways."),
        ("pawn-tuxedo-vest-set.html", "Tuxedo Vest Set", "style-tuxedovest", "assets/img/pawn/tuxedo-vest-set/black/model-1.jpg", "Child model wearing the Checkmatela Tuxedo Vest Set", "The full tuxedo with vest, for the grandest occasions on the calendar."),
    ]
] + [dict(file=c["file"], label=c["label"], id=c["id"], img=None, alt="", text=c["text"]) for c in PLACEHOLDER_PAGES]

# colour family per colourway slug (a new colourway with an unknown slug lands in "Other" until it is added here)
COLOR_FAMILY = {
    "black": "Black", "full-black": "Black",
    "charcoal": "Grey", "shiny-charcoal": "Grey", "gray": "Grey", "light-gray": "Grey", "medium-gray": "Grey",
    "navy": "Blue", "light-navy": "Blue", "royal-blue": "Blue", "sky-blue": "Blue", "indigo": "Blue", "indigo-blue": "Blue",
    "white": "White", "full-white": "White", "white-black": "White",
    "beige-khaki": "Neutral", "khaki": "Neutral",
    "hunter-green": "Green", "burgundy": "Red", "red": "Red",
}
FACETS = [{"key": "color", "label": "Colour", "swatch": True}, {"key": "tone", "label": "Shade"}]
REVIEW_FACETS = [["age", "Age"], ["height", "Height"], ["size", "Size bought"], ["fit", "Fit"], ["occasion", "Occasion"]]

# What each cut includes — used by the "compare the four cuts" table on pawn.html. Verify against the real product specs.
COMPARE = {
    "slim-fit":        dict(jacket=True,  vest=True, trousers=True, shirt=True, tie="Tie",                    best="School events, weddings, church"),
    "suit-vest-set":   dict(jacket=False, vest=True, trousers=True, shirt=True, tie="Tie",                    best="Ring bearers, family photos, warm weather"),
    "tuxedo":          dict(jacket=True,  vest=True, trousers=True, shirt=True, tie="Bow tie",                best="Black tie, prom, formal weddings"),
    "tuxedo-vest-set": dict(jacket=False, vest=True, trousers=True, shirt=True, tie="Tie + pocket square",    best="Black-tie events, weddings, holiday portraits"),
}


def gallery_card(line, slug, name, cfg, eager):
    base = f"assets/img/pawn/{line}/{slug}"
    disk = os.path.join(ROOT, base)
    models = sorted(glob.glob(os.path.join(disk, "model-*.jpg")))
    plains = sorted(glob.glob(os.path.join(disk, "plain-*.jpg")))
    order = [("model", i + 1) for i in range(len(models))] + [("plain", i + 1) for i in range(len(plains))]
    thumbs = []
    for idx, (kind, n) in enumerate(order, 1):
        full = f"{base}/{kind}-{n}.jpg"
        thumb = f"{base}/thumb-{idx}.jpg"
        alt = MODEL_ALTS.get(n, "view") if kind == "model" else PLAIN_ALTS.get(n, "product only")
        active = " is-active" if idx == 1 else ""
        thumbs.append(
            f'          <button class="gallery-thumb{active}" data-src="{full}" aria-label="View {name} {alt}"><img src="{thumb}" alt="" loading="lazy"></button>'
        )
    loading = "" if eager else ' loading="lazy"'
    fam = COLOR_FAMILY.get(slug, "Other")
    hero = os.path.join(ROOT, base, "hero.webp")
    tone = tone_of(swatch_hex(hero)) if os.path.exists(hero) else "Mid"
    plain_name = html.unescape(name)
    return f'''      <div class="gallery-card" data-id="pawn/{line}/{slug}" data-name="{esc(plain_name)}" data-tag="{cfg['label']} &middot; Pawn" data-price="{cfg['price']}" data-img="{base}/model-1.jpg" data-f-color="{fam}" data-f-tone="{tone}">
        <div class="gallery-card__frame">
          <img class="gallery-card__main-img" src="{base}/model-1.jpg" alt="{name} {cfg['label']} — front view on model"{loading}>
          <button type="button" class="cmp-toggle" aria-pressed="false">+ Compare</button>
        </div>
        <div class="gallery-card__thumbs">
{chr(10).join(thumbs)}
        </div>
        <div class="product-card__meta" style="padding:14px 2px 0">
          <div><h4>{name}</h4><span class="piece-tag">{cfg['label']} &middot; Pawn</span></div>
          <span class="product-card__price">${cfg['price']}</span>
        </div>
        <button type="button" class="card-reviews">View details</button>
      </div>'''


def page_head(crumb_html, h1, lead=""):
    """Compact page header for subcategory pages: breadcrumb, title and one line, then straight to the products (no hero — those are for main categories)."""
    return f'''<section class="page-head">
  <div class="container">
    {crumb_html}
    <h1>{h1}</h1>
    {f"<p>{lead}</p>" if lead else ""}
  </div>
</section>'''


def banner_html(line, cfg):
    crumbs = f'<div class="crumbs"><a href="index.html">Home</a> <span>/</span> <a href="pawn.html">Pawn</a> <span>/</span> <span>{cfg["label"]}</span></div>'
    return page_head(crumbs, cfg["label"], cfg["intro"])


def build(line):
    cfg = LINES[line]
    cards = "\n\n".join(gallery_card(line, s, n, cfg, eager=(i < 4)) for i, (s, n) in enumerate(cfg["colors"]))
    other_links = "\n      ".join(f'<a href="{c["file"]}" class="btn ghost">{c["label"]}</a>' for c in LANDING if c["file"] != cfg["file"])
    shop_html = shop_block(cards, FACETS, 'pawn', grid_class='gallery-grid', count_noun='colorways', review_facets=REVIEW_FACETS,
                           extra_attrs=' data-count-suffix=" &middot; sizes 2T&ndash;16 shown" data-options=\'' + KID_OPTIONS + '\'')
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{cfg['title']}</title>
<meta name="description" content="{cfg['meta']}">
{FAVICON}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css?v={CSS_VERSION}">
</head>
<body>

<svg width="0" height="0" style="position:absolute">
  <defs>
{GLYPH_PAWN}
{GLYPH_KING}
  </defs>
</svg>

{ANNOUNCE}

{HEADER}

{banner_html(line, cfg)}

{shop_html}

<section class="section" style="background:var(--pine-deep);color:var(--paper);text-align:center;padding:64px 0">
  <div class="container" data-reveal>
    <span class="eyebrow" style="margin:0 auto">Complete The Set</span>
    <h2 style="margin-top:.4em;font-size:clamp(1.8rem,3vw,2.6rem)">Explore the rest of the Pawn collection.</h2>
    <div style="display:flex;gap:16px;justify-content:center;margin-top:1.8em;flex-wrap:wrap">
      {other_links}
      <a href="pawn.html" class="btn ghost">Back to Pawn</a>
    </div>
  </div>
</section>

{FOOTER}
'''
    html = html.replace('<script src="js/main.js"></script>', '<script src="js/main.js"></script>\n<script src="js/shop.js?v=4"></script>')
    with open(os.path.join(ROOT, cfg["file"]), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", cfg["file"], len(cfg["colors"]), "colorways")


def landing_compare():
    """'Compare the four cuts' table, injected into pawn.html between COMPARE:START/END."""
    def tick(v):
        return '<span class="cmp-yes" aria-label="Included">&#10003;</span>' if v is True else ('<span class="cmp-no" aria-label="Not included">&mdash;</span>' if v is False else v)
    cols = ORDER
    head = "".join(
        f'<th scope="col"><a href="{LINES[k]["file"]}"><img src="assets/img/pawn/{k}/{LINES[k]["hero"][0]}/model-1.jpg" alt="" loading="lazy"><b>{LINES[k]["label"]}</b><span>${LINES[k]["price"]}</span></a></th>' for k in cols)
    rows = [("Colourways", [str(len(LINES[k]["colors"])) for k in cols]), ("Illustrative sizes", ["2T&ndash;16"] * 4),
            ("Jacket", [tick(COMPARE[k]["jacket"]) for k in cols]), ("Vest", [tick(COMPARE[k]["vest"]) for k in cols]),
            ("Trousers", [tick(COMPARE[k]["trousers"]) for k in cols]), ("Shirt", [tick(COMPARE[k]["shirt"]) for k in cols]),
            ("Tie", [COMPARE[k]["tie"] for k in cols]), ("Best for", [COMPARE[k]["best"] for k in cols])]
    body = "".join(f'<tr><th scope="row">{r}</th>' + "".join(f"<td>{c}</td>" for c in cells) + "</tr>" for r, cells in rows)
    cta = "".join(f'<td><a class="btn small" href="{LINES[k]["file"]}">Explore {LINES[k]["label"]}</a></td>' for k in cols)
    return f'''<section class="section compare-section">
  <div class="container">
    <div class="section-head" data-reveal>
      <span class="eyebrow">Compare</span>
      <h2>Which cut is right?</h2>
      <p>The four Pawn styles side by side. Set contents, sizing and prices are preview information; confirm before ordering.</p>
    </div>
    <div class="table-wrap" data-reveal>
      <table class="compare-table">
        <thead><tr><td></td>{head}</tr></thead>
        <tbody>{body}<tr class="compare-cta"><td></td>{cta}</tr></tbody>
      </table>
    </div>
  </div>
</section>'''


def landing_styles():
    options = "\n".join(f'        <option value="{c["file"]}">{c["label"]}{" (coming soon)" if not c["img"] else ""}</option>' for c in LANDING)
    def card(c):
        if c["img"]:
            return f'''      <a class="style-card style-card--live" href="{c["file"]}" id="{c["id"]}">
        <span class="style-card__photo"><img src="{c["img"]}" alt="{c["alt"]}"></span>
        <h4>{c["label"]}</h4>
        <p>{c["text"]}</p>
        <span class="style-card__badge style-card__badge--live">Explore styles →</span>
      </a>'''
        return f'''      <a class="style-card" href="{c["file"]}" id="{c["id"]}">
        <span class="style-card__glyph"><svg viewBox="0 0 100 130" aria-hidden="true"><use href="#glyph-pawn" fill="currentColor"/></svg></span>
        <h4>{c["label"]}</h4>
        <p>{c["text"]}</p>
        <span class="style-card__badge">Coming soon</span>
      </a>'''
    return options, "\n".join(card(c) for c in LANDING)


def build_landing():
    path = os.path.join(ROOT, "pawn.html")
    src = open(path, encoding="utf-8").read()
    src = replace_between(src, "<!-- COMPARE:START -->", "<!-- COMPARE:END -->", landing_compare())
    options, cards = landing_styles()
    src = replace_between(src, "<!-- STYLE-OPTIONS:START -->", "<!-- STYLE-OPTIONS:END -->", '        <option value="">All Styles</option>\n' + options)
    src = replace_between(src, "<!-- STYLE-CARDS:START -->", "<!-- STYLE-CARDS:END -->", cards)
    open(path, "w", encoding="utf-8").write(src)
    print("pawn.html: style cards + compare table")


if __name__ == "__main__":
    for k in ORDER:
        build(k)
    build_landing()
    import gen_nav; gen_nav.main()   # keep the menu, search index and header links in sync with the pages just written
