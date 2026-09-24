"""Generates the four Pawn category pages (pawn-slim-fit / suit-vest-set / tuxedo / tuxedo-vest-set .html).

Run from anywhere:  python3 tools/gen_pawn_pages.py
Reads the processed images under assets/img/pawn/ (see process_pawn_images.py and make_hero_cutouts.py).
"""
import os, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_VERSION = "14"

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
  <a href="index.html" class="brand">
    <span class="glyph"><svg viewBox="0 0 100 100"><use href="#glyph-king" fill="currentColor"/></svg></span>
    Checkmatela
    <small style="margin-left:2px">FORMAL WEAR</small>
  </a>
  <nav class="main-nav" id="mainNav">
    <a href="king.html">King — Men</a>
    <a href="queen.html">Queen — Women</a>
    <div class="nav-item has-dropdown">
      <a href="pawn.html">Pawn — Kids</a>
      <div class="nav-dropdown">
        <a href="pawn-slim-fit.html">Slim Fit</a>
        <a href="pawn-suit-vest-set.html">Suit Vest Set</a>
        <a href="pawn-tuxedo.html">Tuxedo</a>
        <a href="pawn-tuxedo-vest-set.html">Tuxedo Vest Set</a>
      </div>
    </div>
    <a href="bishop.html">Bishop — Accessories</a>
    <a href="rook.html">Rook — Shoes</a>
  </nav>
  <div class="header-actions">
    <button class="icon-btn search-ic" aria-label="Search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg></button>
    <button class="icon-btn" aria-label="Account"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></svg></button>
    <button class="icon-btn" aria-label="Bag"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 8h12l-1 13H7L6 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg></button>
    <button class="nav-toggle" id="navToggle" aria-label="Menu"><span></span><span></span><span></span></button>
  </div>
</header>'''

FOOTER = '''<footer class="site-footer">
  <div class="container footer-top">
    <div class="footer-brand">
      <a href="index.html" class="brand">
        <span class="glyph"><svg viewBox="0 0 100 100"><use href="#glyph-king" fill="currentColor"/></svg></span>
        Checkmatela
      </a>
      <p>Chess-inspired formal wear, tailored for the moments that decide everything. Every move, considered.</p>
      <div class="footer-social">
        <a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1"/></svg></a>
        <a href="#" aria-label="Pinterest"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M9 17c1-4 1-9 3-9s2 3 1 5-3 2-3-1"/></svg></a>
        <a href="#" aria-label="X"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 4l16 16M20 4L4 20"/></svg></a>
      </div>
    </div>
    <div class="footer-col"><h5>The Board</h5><ul>
      <li><a href="king.html">King — Men</a></li>
      <li><a href="queen.html">Queen — Women</a></li>
      <li><a href="pawn.html">Pawn — Kids</a></li>
      <li><a href="bishop.html">Bishop — Accessories</a></li>
      <li><a href="rook.html">Rook — Shoes</a></li>
    </ul></div>
    <div class="footer-col"><h5>Company</h5><ul>
      <li><a href="#">Our Story</a></li><li><a href="#">Master Tailors</a></li><li><a href="#">Sustainability</a></li><li><a href="#">Press</a></li>
    </ul></div>
    <div class="footer-col"><h5>Service</h5><ul>
      <li><a href="#">Book a Fitting</a></li><li><a href="#">Size Guide</a></li><li><a href="#">Alterations</a></li><li><a href="#">Shipping &amp; Returns</a></li>
    </ul></div>
    <div class="footer-col"><h5>Contact</h5><ul>
      <li><a href="mailto:concierge@checkmatela.com">concierge@checkmatela.com</a></li>
      <li><a href="tel:+18885550142">+1 (888) 555-0142</a></li>
      <li>New York · Los Angeles · Toronto</li>
    </ul></div>
  </div>
  <div class="checker-strip"></div>
  <div class="container footer-bottom">
    <span>© 2026 Checkmatela. All moves reserved.</span>
    <div class="legal"><a href="#">Privacy</a><a href="#">Terms</a><a href="#">Accessibility</a></div>
  </div>
</footer>

<script src="js/main.js"></script>
</body>
</html>'''

ANNOUNCE = '''<div class="announce">
  <div class="announce__inner">
    <div class="announce__msgs">
      <a href="pawn.html" style="--n:0">Now open — the Pawn kids collection</a>
      <span style="--n:1">Complimentary alterations on every order</span>
      <span style="--n:2">Free white-glove shipping over $500</span>
    </div>
    <div class="announce__links">
      <a href="tel:+18885550142">+1 (888) 555-0142</a>
      <a href="#">Size Guide</a>
      <a href="#">Book a Fitting</a>
    </div>
  </div>
</div>'''

MODEL_ALTS = {1: "front view on model", 2: "angled pose on model", 3: "back view on model", 4: "trouser detail on model"}
PLAIN_ALTS = {1: "product only, front", 2: "product only, flat detail"}

LINES = {
    "suit-vest-set": dict(
        file="pawn-suit-vest-set.html", label="Suit Vest Set", price=89,
        title="Suit Vest Set — Pawn Kids | Checkmatela",
        meta="Checkmatela Pawn collection — Suit Vest Set for kids, in Black, Indigo, Light Gray and Navy.",
        intro="Jacket-free and effortless — a shirt, vest and trouser set built for a young gentleman who's always on the move. Four colorways, first move ready.",
        colors=[("black", "Black"), ("indigo", "Indigo"), ("light-gray", "Light Gray"), ("navy", "Navy")],
        hero=["black", "indigo", "navy"],
    ),
    "tuxedo-vest-set": dict(
        file="pawn-tuxedo-vest-set.html", label="Tuxedo Vest Set", price=99,
        title="Tuxedo Vest Set — Pawn Kids | Checkmatela",
        meta="Checkmatela Pawn collection — Tuxedo Vest Set for kids, in Black, Burgundy, Light Gray and Light Navy.",
        intro="Black-tie formality, scaled down without cutting a corner — satin-trimmed vest, tie and pocket square for the biggest nights on the calendar. Four colorways.",
        colors=[("black", "Black"), ("burgundy", "Burgundy"), ("light-gray", "Light Gray"), ("light-navy", "Light Navy")],
        hero=["black", "burgundy", "light-navy"],
    ),
    "slim-fit": dict(
        file="pawn-slim-fit.html", label="Slim Fit", price=129,
        title="Slim Fit — Pawn Kids | Checkmatela",
        meta="Checkmatela Pawn collection — Slim Fit suits for kids in fourteen colorways.",
        intro="A tapered, modern cut for the junior gentleman who already knows his angles. Fourteen colorways, sharp from the first move.",
        colors=[("black", "Black"), ("navy", "Navy"), ("charcoal", "Charcoal"), ("light-gray", "Light Gray"),
                ("medium-gray", "Medium Gray"), ("white", "White"), ("beige-khaki", "Beige Khaki"),
                ("khaki", "Khaki"), ("light-navy", "Light Navy"), ("royal-blue", "Royal Blue"),
                ("sky-blue", "Sky Blue"), ("indigo-blue", "Indigo Blue"), ("hunter-green", "Hunter Green"),
                ("burgundy", "Burgundy")],
        hero=["navy", "burgundy", "hunter-green"],
    ),
    "tuxedo": dict(
        file="pawn-tuxedo.html", label="Tuxedo", price=139,
        title="Tuxedo — Pawn Kids | Checkmatela",
        meta="Checkmatela Pawn collection — shawl-lapel tuxedos for kids in twelve colorways.",
        intro="Black-tie formality, sized for the next generation's biggest nights — shawl-lapel jacket, vest and bow tie in twelve colorways.",
        colors=[("full-black", "Full Black"), ("white-black", "White &amp; Black"), ("full-white", "Full White"),
                ("charcoal", "Charcoal"), ("shiny-charcoal", "Shiny Charcoal"), ("gray", "Gray"),
                ("navy", "Navy"), ("royal-blue", "Royal Blue"), ("red", "Red"),
                ("burgundy", "Burgundy"), ("hunter-green", "Hunter Green"), ("khaki", "Khaki")],
        hero=["full-black", "red", "royal-blue"],
    ),
}
ORDER = ["slim-fit", "suit-vest-set", "tuxedo", "tuxedo-vest-set"]


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
    return f'''      <div class="gallery-card">
        <div class="gallery-card__frame">
          <img class="gallery-card__main-img" src="{base}/model-1.jpg" alt="{name} {cfg['label']} — front view on model"{loading}>
        </div>
        <div class="gallery-card__thumbs">
{chr(10).join(thumbs)}
        </div>
        <div class="product-card__meta" style="padding:14px 2px 0">
          <div><h4>{name}</h4><span class="piece-tag">{cfg['label']} &middot; Pawn</span></div>
          <span class="product-card__price">${cfg['price']}</span>
        </div>
      </div>'''


def banner_html(line, cfg):
    figs = []
    for slug in cfg["hero"]:
        rel = f"assets/img/pawn/{line}/{slug}/hero.webp"
        w, h = Image.open(os.path.join(ROOT, rel)).size
        name = dict(cfg["colors"])[slug].replace("&amp;", "&")
        figs.append(f'<img src="{rel}" width="{w}" height="{h}" alt="Child model in the Checkmatela {cfg["label"]}, {name}">')
    figures = "\n      ".join(figs)
    return f'''<section class="cat-hero">
  <div class="cat-hero__bg"></div>
  <div class="cat-hero__fade"></div>
  <div class="cat-hero__inner">
    <div class="cat-hero__copy">
      <div class="crumbs"><a href="index.html">Home</a> <span>/</span> <a href="pawn.html">Pawn</a> <span>/</span> <span>{cfg['label']}</span></div>
      <span class="cat-hero__glyph"><svg viewBox="0 0 100 100"><use href="#glyph-pawn" fill="currentColor"/></svg></span>
      <h1>{cfg['label']}</h1>
      <p>{cfg['intro']}</p>
    </div>
    <div class="cat-hero__figures">
      {figures}
    </div>
  </div>
</section>'''


def build(line):
    cfg = LINES[line]
    cards = "\n\n".join(gallery_card(line, s, n, cfg, eager=(i < 4)) for i, (s, n) in enumerate(cfg["colors"]))
    others = [k for k in ORDER if k != line]
    other_links = "\n      ".join(f'<a href="{LINES[k]["file"]}" class="btn ghost">{LINES[k]["label"]}</a>' for k in others)
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{cfg['title']}</title>
<meta name="description" content="{cfg['meta']}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%230c0c0d%22/><text x=%2250%22 y=%2268%22 font-size=%2264%22 text-anchor=%22middle%22 fill=%22%23d9b876%22>&#9823;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
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

<div class="container">
  <div class="filter-bar">
    <span class="filter-bar__count">{len(cfg['colors'])} colorways &middot; sizes 2T&ndash;14</span>
    <span class="filter-bar__sort">
      Sort by
      <select>
        <option>Featured</option>
        <option>Price: Low to High</option>
        <option>Price: High to Low</option>
      </select>
    </span>
  </div>
</div>

<section class="section" style="padding-top:40px">
  <div class="container">
    <div class="gallery-grid" data-reveal-group>
{cards}
    </div>
  </div>
</section>

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
    with open(os.path.join(ROOT, cfg["file"]), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", cfg["file"], len(cfg["colors"]), "colorways")


if __name__ == "__main__":
    for k in ORDER:
        build(k)
