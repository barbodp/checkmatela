"""Builds the Discover pages that are not plain info pages: the Style Guide blog (blog.html + one page per article), the Lookbook, Reviews and the FAQ.

All of them are subcategories of Discover, so they use the compact header (no hero). Copy is ours (general styling advice and our own policies);
the lookbook is assembled from real catalog pieces (tools/gen_antonio.py ITEMS); the reviews page does not invent reviews.
Run:  python3 tools/gen_discover.py   (gen_info_pages.py and gen_antonio.py call it; gen_nav.py indexes the pages afterwards)
"""
import os, json, datetime
from gen_info_pages import PAGES, build, section, cta, steps, faq, table, EMAIL, PHONE_DISPLAY, PHONE_TEL
import gen_info_pages as info

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
BLOG = "blog.html"
EMAIL_LINK = f'<a class="link" href="mailto:{EMAIL}">{EMAIL}</a>'


def L(href, text):
    return f'<a class="link" href="{href}">{text}</a>'


def prose(*paras):
    return '<div class="prose">' + "".join(f"<p>{p}</p>" for p in paras) + "</div>"


def bullets(items):
    return '<ul class="prose-list">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


# ------------------------------------------------------------------ Style Guide (blog)
POSTS = [
    dict(slug="what-to-wear-to-a-wedding", title="What to wear to a wedding", img="assets/img/categories/men-model.webp",
         summary="Decode the dress code, pick a color that works in any room and check the fit before the day.",
         sections=[
             ("Start with the dress code.", prose("The invitation usually tells you what to wear. Read it first, then match the formality.") + bullets([
                 "<b>Black tie:</b> a tuxedo with a bow tie, or a very dark formal suit if you do not own one.",
                 "<b>Formal or black-tie optional:</b> a dark suit or a tuxedo, with a tie and polished shoes.",
                 "<b>Cocktail or semi-formal:</b> a suit in navy, charcoal or grey, with a tie or a pocket square.",
                 "<b>Casual, garden or summer:</b> a lighter suit such as beige or light grey. A tie is optional if the invitation says so."]), "Dress code"),
             ("Choose the color.", prose("Navy and charcoal are safe for almost any wedding, day or night. Lighter colors suit summer and daytime ceremonies; darker colors suit evening. Leave white, ivory and cream to the couple unless the invitation asks for them."), "Color"),
             ("Check the fit.", prose("A good fit matters more than the price tag. The shoulder seam should sit at the edge of your shoulder, the jacket should cover the seat of your trousers, and about half an inch of shirt cuff should show at the wrist. Trousers should rest on your shoes without bunching.",
                                      f"Every {L('antonio-uomo.html', 'Antonio Uomo')} piece has a size chart pop-up under the size picker, and our {L('alterations.html', 'alterations page')} explains what we can adjust."), "Fit"),
             ("Leave time.", prose(f"Order early enough to try the full outfit on, swap a size if needed and fit in any alterations. Our {L('shipping-returns.html', 'exchange and return terms')} are simple, but they work best when you are not trying everything the night before."), "Timing"),
         ],
         shop=[("Wedding looks", "king.html?occasion=Wedding"), ("Summer looks", "king.html?occasion=Summer"), ("Find your look", "find-your-look.html")]),
    dict(slug="tuxedo-vs-suit", title="Tuxedo or suit: how to choose", img="assets/img/categories/king-men.jpg",
         summary="What actually separates a tuxedo from a suit, and which one the occasion calls for.",
         sections=[
             ("The real differences.", prose("A tuxedo is built for evening. Traditionally it has satin or contrast lapels, satin-covered buttons and trousers with a satin stripe, and it is worn with a bow tie. A suit is made of one cloth throughout, with a standard collar and buttons, and is worn with a necktie or open collar."), "Basics"),
             ("Which one should you wear?", table(["Occasion", "Best choice"], [
                 ["Black tie, gala, opera", "Tuxedo"], ["Formal evening wedding", "Tuxedo or a dark three-piece suit"], ["Daytime or summer wedding", "Suit, often in a lighter color"],
                 ["Prom", "Tuxedo or a statement suit"], ["Business or interview", "Suit"]], "A simple guide, not a rule"), "Choosing"),
             ("Color and style.", prose("Black and midnight blue are the classic tuxedo colors, and they photograph well. Burgundy, royal blue and other colors are popular for prom and modern weddings. If the invitation says black tie, stay with black, midnight or a very dark shade."), "Color"),
             ("Shop both.", prose(f"Browse our {L('king.html?style=Tuxedo', 'tuxedos')} (two- and three-piece) or our {L('king.html?style=Three-piece', 'three-piece suits')}, and use the filters to narrow by color, pattern and occasion."), "Next step"),
         ],
         shop=[("Tuxedos", "king.html?style=Tuxedo"), ("Three-piece suits", "king.html?style=Three-piece"), ("Black tie", "king.html?occasion=Black%20tie")]),
    dict(slug="how-to-measure-for-a-suit", title="How to measure for a suit", img="assets/img/products/english-opening-charcoal.jpg",
         summary="Five measurements, a tape and ten minutes: how to find your size before you order.",
         sections=[
             ("What you need.", prose("A soft tape measure and, ideally, someone to help. Wear a thin shirt rather than a coat, stand naturally and keep the tape snug but not tight."), "Before you start"),
             ("The measurements.", steps([("Chest", "Around the fullest part of your chest, under your arms."), ("Waist", "Around your natural waist, just above the hip bones."),
                                         ("Shoulder", "Across the back from one shoulder seam to the other."), ("Sleeve", "From the shoulder seam to the wrist bone, arm relaxed."),
                                         ("Inseam", "From the crotch to where you want the trouser hem to land, wearing the shoes you will wear.")]), "Measure"),
             ("Choosing the size.", prose("Our Antonio Uomo size chart asks you to choose a jacket chest at least 2 to 3 inches bigger than your own chest, measured without outerwear. That gives you room for a shirt and vest and a comfortable fit.",
                                          "For length, choose Short, Regular or Long to match your height. If you are between sizes, go up in the jacket and have it tailored, because a jacket is harder to alter than trousers."), "Sizing"),
             ("Check the chart on the piece.", prose(f"Each piece has its own chart in a pop-up under the size picker, with every measurement. Questions? {L('book-a-fitting.html', 'Ask about fit')} and we will help you choose."), "Next step"),
         ],
         shop=[("Shop all men", "king.html"), ("Ask about fit", "book-a-fitting.html"), ("Alterations", "alterations.html")]),
    dict(slug="groomsmen-suit-guide", title="A groomsmen suit guide", img="assets/img/products/sicilian-onyx-tux.jpg",
         summary="Pick the look, collect the sizes and keep the whole party on schedule.",
         sections=[
             ("Decide on the look.", prose("Most wedding parties go one of two ways: everyone in the same suit, or everyone in the same color with small differences such as a vest, tie or pocket square for the groom. Same-suit is simplest and looks best in photos."), "The look"),
             ("Collect sizes early.", prose(f"The biggest delays come from sizes. Send every groomsman our {L('how-to-measure-for-a-suit.html', 'measuring guide')}, ask for chest, waist, sleeve and inseam, and have each person check the size chart for the exact piece."), "Sizes"),
             ("Mind the timeline.", bullets(["Choose the suit as soon as the party is set.", "Confirm everyone's sizes before you order.", "Order early enough to allow for one exchange and any alterations.", "Try everything on well before the wedding."]), "Timing"),
             ("Group savings.", prose(f"Ordering together can save money. Our group discount is applied in the bag when your order qualifies, and {L('book-a-fitting.html', 'we are happy to confirm')} what applies to the pieces you choose."), "Savings"),
         ],
         shop=[("Wedding looks", "king.html?occasion=Wedding"), ("Tuxedos", "king.html?style=Tuxedo"), ("Ask about fit", "book-a-fitting.html")]),
    dict(slug="dressing-kids-for-formal-events", title="Dressing kids for formal events", img="assets/img/categories/kids-model.webp",
         summary="Comfort, fit and the right set for ring bearers, page boys and every family photo.",
         sections=[
             ("Comfort comes first.", prose("A child who is comfortable behaves better and looks better. Choose soft linings and room to move, and let your child try the outfit on at home before the day."), "Comfort"),
             ("Choose the set.", prose(f"A full suit or tuxedo suits formal ceremonies. A {L('pawn-suit-vest-set.html', 'vest set')} is cooler and easier for warm weather, family photos and ring bearers. See the {L('pawn.html', 'Pawn collection')} to compare the cuts side by side."), "Sets"),
             ("Get the fit right.", prose(f"Use the age as a starting point, then check the real measurements in our {L('size-guide.html', 'size guide')}. A little room is fine, but sleeves and trousers that are too long look sloppy and can trip a small child. Boys in larger sizes can shop the {L('pawn-husky.html', 'Husky Fit')} page."), "Fit"),
             ("Match the party.", prose("Match the color to the wedding party, or pick a neutral such as navy, black or grey. Keep shoes simple and comfortable."), "Style"),
         ],
         shop=[("Kids' formal wear", "pawn.html"), ("Vest sets", "pawn-suit-vest-set.html"), ("Kids' size guide", "size-guide.html")]),
]


def post_url(p):
    return f"blog-{p['slug']}.html"


def build_blog():
    cards = "".join(f'''<a class="post-card" href="{post_url(p)}"><span class="post-card__img"><img src="{p["img"]}" alt="" loading="lazy"></span><span class="post-card__body"><b>{p["title"]}</b><span>{p["summary"]}</span><em>Read the guide &rarr;</em></span></a>''' for p in POSTS)
    PAGES["blog"] = dict(glyph="glyph-king", crumb="Style Guide", h1="Style Guide", compact=True,
        lead="Plain-language guides to dress codes, fit and sizing, for weddings, proms and everything in between.",
        meta="Checkmatela style guide: what to wear to a wedding, tuxedo vs suit, how to measure for a suit and more.",
        body=[section("Guides for every event.", f'<div class="post-grid">{cards}</div>', "Style Guide"),
              cta("Not sure where to start?", "find-your-look.html", "Find your look")])
    build("blog", PAGES["blog"])
    for p in POSTS:
        slug = "blog-" + p["slug"]
        links = "".join(f'<a class="btn ghost" href="{h}">{t}</a>' for t, h in p["shop"])
        body = [section(h, inner, eb, alt=bool(i % 2)) for i, (h, inner, eb) in enumerate(p["sections"])]
        body.append(f'<section class="info-cta"><div class="container" data-reveal><h2>Ready to shop?</h2><div class="cta-row">{links}</div></div></section>')
        PAGES[slug] = dict(glyph="glyph-king", crumb=p["title"], parent=("Style Guide", BLOG), h1=p["title"], lead=p["summary"], compact=True,
                           meta=p["summary"], body=body)
        build(slug, PAGES[slug])
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "description": p["summary"], "datePublished": TODAY,
              "author": {"@type": "Organization", "name": "Checkmatela"}, "publisher": {"@type": "Organization", "name": "Checkmatela"}}
        inject_ld(slug + ".html", ld)


# ------------------------------------------------------------------ FAQ
FAQS = [
    ("Ordering", [
        ("Can I order online today?", f"Not yet. The site is a preview: you can build a bag and walk through a checkout preview, but no payment is taken and no order is placed. To plan an event or ask about timing, {L('book-a-fitting.html', 'send us a note')} or call {L('tel:' + PHONE_TEL, PHONE_DISPLAY)}."),
        ("Are the prices final?", "Prices shown are previews and may change before ordering opens. We will confirm price, availability and delivery before you pay."),
    ]),
    ("Sizing and fit", [
        ("How do I find my size?", f"Every Antonio Uomo piece has a size chart pop-up under the size picker with full measurements, and our {L('how-to-measure-for-a-suit.html', 'measuring guide')} shows how to take them. Choose a jacket chest 2 to 3 inches bigger than your own."),
        ("What if I am between sizes?", "Go up in the jacket and have it tailored. A jacket is harder to alter than trousers."),
        ("What are Short, Regular and Long?", "They are jacket lengths. Choose the one that matches your height; the chart on each piece shows the measurements."),
        ("Do you have kids' sizes?", f"Yes, sizes 2T to 16 in the {L('pawn.html', 'Pawn collection')}, with a roomier {L('pawn-husky.html', 'husky fit')} range in larger sizes. See the {L('size-guide.html', 'size guide')} for measurements."),
    ]),
    ("Shipping", [
        ("How much is shipping?", "Standard shipping is $18 and free on orders over $500. Express shipping is $35. Local pickup in Los Angeles is free. Exact delivery windows are confirmed at checkout."),
    ]),
    ("Returns and exchanges", [
        ("What is the return window?", "14 days from delivery for suits, tuxedos, individual pieces and dresses, and 30 days for accessories and shoes."),
        ("Are exchanges free?", "Yes, once per item. A refund, or a second exchange on an item that has already used its free one, has a flat $12 return-shipping fee. If we send the wrong or a damaged item, return shipping is free."),
        ("What condition must an item be in?", f"Unworn and unwashed with tags attached, no odor or marks, vents and pockets still stitched on jackets, shoes tried on indoors only, and not altered. See the full {L('shipping-returns.html', 'shipping and returns page')}."),
    ]),
    ("Alterations", [
        ("Do you offer alterations?", f"Every suit and dress purchase includes one complimentary round of alterations through our Los Angeles studio or a fitting appointment. Further tailoring is billed at cost. Read more on the {L('alterations.html', 'alterations page')}."),
    ]),
    ("Groups and offers", [
        ("Is there a groomsmen discount?", "Yes. Our group discount is applied in the bag when your order qualifies, with a bigger discount for larger parties. Ask us and we will confirm what applies to your pieces."),
        ("Do you have promo codes?", "Sometimes. Codes are entered at checkout, and the checkout preview shows how they will work."),
    ]),
    ("Care", [
        ("How do I care for a suit?", "Most of our suits are dry clean only. Check the details on each product page and the care label on the garment."),
    ]),
]


def build_faq():
    secs = []
    for i, (title, qa) in enumerate(FAQS):
        secs.append(section(title + ".", faq(qa), "FAQ", alt=bool(i % 2)))
    secs.append(cta("Still have a question?", "book-a-fitting.html", "Ask us"))
    PAGES["faq"] = dict(glyph="glyph-king", crumb="FAQ", h1="Frequently asked questions", compact=True,
        lead="Quick answers about sizing, shipping, returns and alterations.", meta="Checkmatela FAQ: sizing, shipping, returns, exchanges, alterations and group offers.", body=secs)
    build("faq", PAGES["faq"])
    import re
    plain = lambda s: re.sub(r"<[^>]+>", "", s)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for _, qa in FAQS for q, a in qa]}
    inject_ld("faq.html", ld)


# ------------------------------------------------------------------ Reviews (no invented reviews)
def build_reviews():
    PAGES["reviews"] = dict(glyph="glyph-king", crumb="Reviews", h1="Reviews", compact=True,
        lead="Real reviews from real customers, once orders open.", meta="Checkmatela reviews: how verified customer reviews will work.",
        body=[
            section("No reviews yet.", prose("Checkmatela is still in preview, so we do not have customer reviews to show, and we will not make any up. Once orders open, every review on the site will come from a customer who bought the piece."), "Where we are"),
            section("What a review will include.", steps([("Rating and a few words", "Stars, a title and your thoughts on the piece."), ("Fit details", "Your height, build and the size you bought, so the next customer can compare."),
                                                         ("Verified purchase", "Reviews are tied to an order, and we show them on the product they are about.")]), "How reviews will work", alt=True),
            section("Tried a piece? Tell us.", prose(f"If you have bought from us or fitted a piece in the studio, we would love to hear how it went. {EMAIL_LINK} with your review and we will share it with your permission."), "Share your experience"),
            cta("Looking for your look?", "king.html", "Shop all men"),
        ])
    build("reviews", PAGES["reviews"])


# ------------------------------------------------------------------ Lookbook (real catalog pieces)
LOOKS = [
    ("Weddings", "Navy and grey for the ceremony, lighter tones for the garden party.", "king.html?occasion=Wedding",
     [("3 Piece Slim Fit Suits", "Navy"), ("3 Piece Slim Fit Suits", "Light Grey"), ("Plaid Suits", "Blue"), ("3 Piece Classic Fit Suits", "Charcoal"), ("3 Piece Slim Fit Suits", "Stone"), ("2 Piece Slim Fit Suits", "Beige")]),
    ("Black tie", "Black, midnight and burgundy tuxedos for the evening.", "king.html?occasion=Black%20tie",
     [("3 Piece Tuxedo", "Black"), ("2 Piece Tuxedo", "Black"), ("3 Piece Tuxedo", "Midnight Blue"), ("2 Piece Tuxedo", "Bordeaux"), ("3 Piece Tuxedo", "White"), ("2 Piece Tuxedo", "Graphite")]),
    ("Prom", "Color, shine and a little attitude.", "king.html?occasion=Prom",
     [("3 Piece Tuxedo", "Burgundy"), ("2 Piece Tuxedo", "Royal Blue"), ("Jackets", "Shiny Gold"), ("3 Piece Tuxedo", "Navy"), ("Textured Suits", "Dark Teal"), ("Jackets", "Shiny Silver")]),
    ("Business", "Sharp suits that work from the first meeting to the last.", "king.html?occasion=Business",
     [("2 Piece Slim Fit Suits", "Charcoal"), ("3 Piece Classic Fit Suits", "Navy"), ("Plaid Suits", "Charcoal"), ("3 Piece Slim Fit Suits", "Black"), ("2 Piece Slim Fit Suits", "True Grey"), ("Pants", "Charcoal")]),
    ("Summer", "Light colors for warm days and outdoor ceremonies.", "king.html?occasion=Summer",
     [("3 Piece Slim Fit Suits", "Light Blue"), ("3 Piece Slim Fit Suits", "Dove Grey"), ("2 Piece Slim Fit Suits", "Beige")]),
]
KIDS_LOOKS = [("Slim Fit in navy", "pawn-slim-fit.html", "assets/img/pawn/slim-fit/navy/model-1.jpg"), ("Tuxedo in white and black", "pawn-tuxedo.html", "assets/img/pawn/tuxedo/white-black/model-1.jpg"),
              ("Suit Vest Set in black", "pawn-suit-vest-set.html", "assets/img/pawn/suit-vest-set/black/model-1.jpg")]


def build_lookbook():
    import gen_antonio as au
    ordered = au.sorted_items(au.ITEMS)
    secs = []
    for i, (title, line, href, specs) in enumerate(LOOKS):
        picks = []
        for ty, col in specs:
            hit = next((it for it in ordered if it["type"] == ty and it["colour"] == col), None)
            if hit:
                picks.append(hit)
        cards = "\n".join(au.card(p, facets=False) for p in picks)
        secs.append(section(title + ".", f'<p class="look-note">{line}</p><div class="product-grid look-grid">{cards}</div><p class="look-more"><a class="btn dark-ghost" href="{href}">Shop all {title.lower()} looks</a></p>', "Lookbook", alt=bool(i % 2)))
    kids = "".join(f'<a class="product-card au-card" href="{h}"><span class="au-card__img"><img src="{img}" alt="{t}" loading="lazy" width="480" height="720"></span><div class="product-card__meta"><div><h4>{t}</h4><span class="piece-tag">Pawn &middot; Kids</span></div></div></a>' for t, h, img in KIDS_LOOKS)
    secs.append(section("Kids.", f'<p class="look-note">Matching sets for ring bearers, page boys and family photos.</p><div class="product-grid look-grid">{kids}</div><p class="look-more"><a class="btn dark-ghost" href="pawn.html">Shop kids\' formal wear</a></p>', "Lookbook", alt=bool(len(LOOKS) % 2)))
    PAGES["lookbook"] = dict(glyph="glyph-king", crumb="Lookbook", h1="Lookbook", compact=True,
        lead="Pieces from the collection, grouped by the occasion they were made for.", meta="Checkmatela lookbook: suits and tuxedos for weddings, black tie, prom, business and summer, plus kids' formal wear.", body=secs)
    build("lookbook", PAGES["lookbook"])


def inject_ld(file, obj):
    path = os.path.join(ROOT, file)
    t = open(path, encoding="utf-8").read()
    tag = '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>\n"
    open(path, "w", encoding="utf-8").write(t.replace("</head>", tag + "</head>", 1))


def main():
    build_blog()
    build_faq()
    build_reviews()
    build_lookbook()
    print("discover:", 1 + len(POSTS), "blog pages, faq, reviews, lookbook")


if __name__ == "__main__":
    main()
    import gen_nav
    gen_nav.main()
