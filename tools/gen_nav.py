"""Builds js/search-index.js — the data behind the site search and the menu's "Build your look" counts (js/nav.js).

It reads the already-generated pages (king.html, the four pawn-*.html pages, bishop.html, rook.html) so products stay in sync
automatically, and adds a curated list of pages and help answers (PAGES / HELP below).

It also stamps a schema.org BreadcrumbList (JSON-LD) into every page that has a visible .crumbs trail.

Run AFTER gen_king_page.py / gen_pawn_pages.py / gen_info_pages.py (they rewrite their pages):   python3 tools/gen_nav.py
"""
import os, re, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
unesc = html.unescape


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


def cards(page, kind):
    out = []
    for m in re.finditer(r'<div class="(?:product-card|gallery-card)"([^>]*data-id="[^"]*"[^>]*)>', read(page)):
        a = dict(re.findall(r'data-([a-z-]+)="([^"]*)"', m.group(1)))
        f = {k[2:]: unesc(v) for k, v in a.items() if k.startswith("f-")}
        out.append(dict(k=kind, t=unesc(a["name"]), s=unesc(a["tag"]).replace("·", "·"), u=page, p=int(a["price"]), i=a["img"], f=f, id=a["id"]))
    return out


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", unesc(s).lower()).strip("-")


def static_cards(page, kind):
    """Bishop / Rook cards are hand-written; stamp an id on each so menu + search links can jump straight to the piece."""
    text = read(page)
    out = []
    for m in re.finditer(r'<a class="product-card"([^>]*)>(.*?)</a>', text, re.S):
        b = m.group(2)
        name = re.search(r"<h4>(.*?)</h4>", b).group(1)
        tag = re.search(r'class="piece-tag">(.*?)<', b).group(1)
        price = int(re.search(r'product-card__price">\$(\d+)', b).group(1))
        img = re.search(r'<img src="([^"]+)"', b).group(1)
        out.append(dict(k=kind, t=unesc(name), s=unesc(tag), u=f"{page}#{slug(name)}", p=price, i=img, f={}))
        if ' id="' not in m.group(1):
            text = text.replace(m.group(0), m.group(0).replace('<a class="product-card"', f'<a class="product-card" id="{slug(name)}"', 1), 1)
    with open(os.path.join(ROOT, page), "w", encoding="utf-8") as f:
        f.write(text)
    return out


# Departments. ONE LINE PER CATEGORY: add a line here when a new category exists (e.g. dict(key="knight", prefix="knight", label="Ties", sub="Knight", landing="knight.html")).
# Every <prefix>.html / <prefix>-*.html page that lists products is discovered automatically — a new Pawn or King page needs no edit anywhere.
DEPTS = [
    dict(key="king", prefix="king", label="Men", sub="King", landing="king.html"),
    dict(key="queen", prefix="queen", label="Women", sub="Queen", landing="queen.html"),
    dict(key="pawn", prefix="pawn", label="Kids", sub="Pawn", landing="pawn.html"),
    dict(key="bishop", prefix="bishop", label="Accessories", sub="Bishop", landing="bishop.html"),
    dict(key="rook", prefix="rook", label="Shoes", sub="Rook", landing="rook.html"),
]
DISCOVER = ("discover", "Discover", "find-your-look.html")


def dept_files(d):
    pat = re.compile(rf"{re.escape(d['prefix'])}(-[a-z0-9-]+)?\.html")
    files = sorted(f for f in os.listdir(ROOT) if pat.fullmatch(f))
    return sorted(files, key=lambda f: (f != d["landing"], f[:-5]))


def page_label(text, fallback):
    m = re.search(r'<div class="crumbs">.*?<span>(?!/)([^<]*)</span>\s*</div>', text, re.S)
    return unesc(m.group(1)).strip() if m else fallback


# (title, url, section label, keywords) — keywords are what people might type
PAGES = [
    ("King — Men's suits & tuxedos", "king.html", "Men", "men mens suits tuxedo tux three-piece two-piece groom groomsmen wedding business prom black tie king"),
    ("Queen — Women's collection", "queen.html", "Women", "women womens dresses gowns bridesmaid queen coming soon"),
    ("Pawn — Kids' formal wear", "pawn.html", "Kids", "kids boys children suits tuxedo ring bearer pawn vest"),
    ("Bishop — Accessories", "bishop.html", "Accessories", "accessories bow tie cufflinks pocket square belt bishop"),
    ("Rook — Shoes", "rook.html", "Shoes", "shoes oxford loafers dress shoes footwear rook"),
    ("Find Your Look", "find-your-look.html", "Plan", "occasion quiz finder help choose recommend style event date measurements"),
    ("Ask About Fit — Book a fitting", "book-a-fitting.html", "Help", "fit fitting appointment contact enquiry email question measurements book"),
    ("Size Guide", "size-guide.html", "Help", "size sizing chart measure measurements chest waist inseam height kids size"),
    ("Alterations", "alterations.html", "Help", "alterations tailoring hem trousers sleeves one free round complimentary"),
    ("Shipping & Returns", "shipping-returns.html", "Help", "shipping returns refund exchange policy delivery free shipping 14 days 30 days"),
    ("Master Tailors — Fit & tailoring", "master-tailors.html", "Company", "tailors tailoring fit shoulders sleeves jacket"),
    ("Our Story", "our-story.html", "Company", "about story why checkmatela brand affordable one place"),
    ("Sustainability — Our approach", "sustainability.html", "Company", "sustainability approach rewear care repair"),
    ("Press", "press.html", "Company", "press media logo brand assets contact journalists"),
    ("Checkout preview", "checkout.html", "Bag", "checkout bag cart pay order promo code"),
]

HELP = [
    ("Groomsmen & wedding-party discount", "king.html?occasion=Wedding", "Save 10% on 3+ suits, 15% on 6+", "groomsmen groom wedding party bulk group discount save 10% 15% bridal"),
    ("Free exchanges", "shipping-returns.html", "Free once per item", "exchange swap size color free exchange"),
    ("Returns & refunds", "shipping-returns.html", "14 days suits, 30 days accessories & shoes", "return refund money back policy 14 day 30 day fee $12"),
    ("One free alteration", "alterations.html", "Included with every suit", "free alteration tailoring hem included complimentary"),
    ("Free shipping over $500", "shipping-returns.html", "Standard shipping $18 under $500", "shipping delivery free over 500 express pickup los angeles"),
    ("Promo codes", "checkout.html", "Enter at checkout", "promo code welcome10 nextmove10 refer20 discount coupon"),
    ("Call or email us", "book-a-fitting.html", "+1 (310) 890-6991 · suit.shop.dtla@gmail.com", "phone call email contact support help los angeles studio"),
]


SITE = "https://checkmatela.vercel.app/"
LD_RE = re.compile(r'<script type="application/ld\+json" data-crumbs>.*?</script>\n?', re.S)


def stamp_breadcrumbs():
    n = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html"):
            continue
        t = read(name)
        m = re.search(r'<div class="crumbs">(.*?)</div>', t, re.S)
        if not m:
            continue
        items = [(unesc(re.sub(r"<[^>]+>", "", x)).strip(), href) for href, x in re.findall(r'<a href="([^"]+)">(.*?)</a>', m.group(1))]
        last = re.findall(r"<span>(?!/)(.*?)</span>", m.group(1))
        if last and last[-1].strip() != "/":
            items.append((unesc(last[-1]).strip(), name))
        ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": nm, "item": SITE + (href if href != "index.html" else "")} for i, (nm, href) in enumerate(items)]}
        tag = '<script type="application/ld+json" data-crumbs>' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + "</script>\n"
        t = LD_RE.sub("", t).replace("</head>", tag + "</head>", 1)
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(t)
        n += 1
    print("breadcrumb JSON-LD stamped on", n, "pages")


NAV_RE = re.compile(r'<nav class="main-nav" id="mainNav"[^>]*>.*?</nav>', re.S)


def stamp_header_nav():
    """Rewrites the header's category links on every page from DEPTS, so a new department shows up in the header everywhere."""
    links = "\n".join(f'      <a href="{d["landing"]}" data-mega="{d["key"]}">{d["label"]}</a>' for d in DEPTS)
    links += f'\n      <a href="{DISCOVER[2]}" data-mega="{DISCOVER[0]}">{DISCOVER[1]}</a>'
    nav = f'<nav class="main-nav" id="mainNav" aria-label="Main">\n{links}\n    </nav>'
    n = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html"):
            continue
        t = read(name)
        if NAV_RE.search(t) and NAV_RE.search(t).group(0) != nav:
            with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
                f.write(NAV_RE.sub(lambda m: nav, t, count=1))
            n += 1
    print("header nav refreshed on", n, "pages")


def main():
    products, nav = [], []
    for d in DEPTS:
        pages, total = [], 0
        for f in dept_files(d):
            text = read(f)
            if 'class="cat-hero' not in text:
                continue
            found = cards(f, d["sub"]) or static_cards(f, d["sub"])
            label = page_label(text, d["label"] if f == d["landing"] else f)
            for c in found:
                c["d"] = d["label"]
                if f != d["landing"]:
                    c["t"], c["s"] = f"{label} — {c['t']}", f"{d['sub']} · {d['label']}"
                products.append(c)
            total += len(found)
            pages.append(dict(t=label, u=f, n=len(found), p=min([c["p"] for c in found], default=0), landing=f == d["landing"]))
        nav.append(dict(key=d["key"], label=d["label"], sub=d["sub"], href=d["landing"], total=total, pages=pages))
    index = {
        "products": products,
        "nav": nav,
        "pages": [dict(t=t, u=u, s=s, kw=kw) for t, u, s, kw in PAGES],
        "help": [dict(t=t, u=u, s=s, kw=kw) for t, u, s, kw in HELP],
    }
    out = os.path.join(ROOT, "js", "search-index.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("/* generated by tools/gen_nav.py — do not edit by hand */\nwindow.CHECKMATELA_INDEX = " + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ";\n")
    import hashlib
    stamp = hashlib.md5(open(out, "rb").read()).hexdigest()[:8]          # cache-bust the index whenever its content changes
    navjs = os.path.join(ROOT, "js", "nav.js")
    src = open(navjs, encoding="utf-8").read()
    open(navjs, "w", encoding="utf-8").write(re.sub(r"search-index\.js\?v=[A-Za-z0-9]+", f"search-index.js?v={stamp}", src))
    print("wrote js/search-index.js:", len(products), "products,", sum(len(d["pages"]) for d in nav), "department pages,", len(PAGES), "pages,", len(HELP), "help answers")
    stamp_header_nav()
    stamp_breadcrumbs()


if __name__ == "__main__":
    main()
