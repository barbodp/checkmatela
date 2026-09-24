"""Generates the eight footer pages (Company + Service): our-story, master-tailors, sustainability, press,
book-a-fitting, size-guide, alterations, shipping-returns  .html

They share the site header / footer / announcement bar with the Pawn pages (imported from gen_pawn_pages.py)
and use the same `.cat-hero` glyph hero as Queen. Copy is placeholder concept copy — edit the PAGES config below,
then run:  python3 tools/gen_info_pages.py
"""
import os, re
from gen_pawn_pages import HEADER, FOOTER, ANNOUNCE, CSS_VERSION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL = "suit.shop.dtla@gmail.com"
PHONE_DISPLAY, PHONE_TEL = "+1 (310) 890-6991", "+13108906991"


def glyph_defs(ids):
    idx = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    out = []
    for i in ids:
        m = re.search(rf'<symbol id="{i}".*?</symbol>', idx, re.S)
        out.append("    " + m.group(0))
    return "\n".join(out)


def cards(items):
    return '<div class="info-grid">' + "".join(
        f'<div class="info-card"><span class="info-card__n">{n}</span><h3>{t}</h3><p>{p}</p></div>'
        for n, t, p in items) + "</div>"


def steps(items):
    return '<ol class="steps">' + "".join(f"<li><h3>{t}</h3><p>{p}</p></li>" for t, p in items) + "</ol>"


def faq(items):
    return '<div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items) + "</div>"


def table(head, rows, caption=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    cap = f"<caption>{caption}</caption>" if caption else ""
    return f'<div class="table-wrap"><table class="size-table">{cap}<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def section(title, inner, eyebrow=None, alt=False):
    eb = f'<span class="eyebrow">{eyebrow}</span>' if eyebrow else ""
    return f'''<section class="info-section{" info-section--alt" if alt else ""}">
  <div class="container">
    <div class="section-head" data-reveal>{eb}<h2>{title}</h2></div>
    <div data-reveal>{inner}</div>
  </div>
</section>'''


def cta(text, href, label):
    return f'''<section class="info-cta">
  <div class="container" data-reveal>
    <h2>{text}</h2>
    <a href="{href}" class="btn">{label}</a>
  </div>
</section>'''


PAGES = {}

PAGES["our-story"] = dict(
    glyph="glyph-king", crumb="Our Story", h1="Our Story",
    lead="Checkmatela began with a simple idea: dressing well is a matter of strategy. Every move considered, every detail placed with intent.",
    meta="The story behind Checkmatela — chess-inspired formal wear made in Los Angeles.",
    body=[
        section("Formal wear, played like a game.", '''<div class="prose">
<p>We are a Los Angeles formal wear house named for the oldest game of strategy. A grandmaster does not rush a move — and neither does a good tailor. Every suit in the Checkmatela collection is named for an opening, cut for the moment that decides everything, and finished by hand.</p>
<p>The pieces of the board became our departments: the <strong>King</strong> for men, the <strong>Queen</strong> for women, the <strong>Pawn</strong> for the next generation, the <strong>Bishop</strong> for the accessories that finish a look on the diagonal, and the <strong>Rook</strong> for the shoes that hold everything up.</p></div>''', "The idea"),
        section("What we believe.", cards([
            ("01", "Considered, not loud", "A jacket should make the man look composed, never costumed. We chase fit and proportion before anything else."),
            ("02", "Ready for the big night", "Weddings, galas, graduations, first communions. Our collection is built for the occasions people remember."),
            ("03", "Formal wear for the whole family", "From a boy's first suit to a man's tuxedo, every piece is cut with the same attention to detail."),
        ]), "Principles", alt=True),
        section("The opening moves.", steps([
            ("The first collection", "Ten men's openings — from the Sicilian tuxedo to the Scotch Game three-piece — each named for a classic chess line."),
            ("The Pawn line opens", "Four kids' styles in 34 colourways: Slim Fit, Suit Vest Set, Tuxedo and Tuxedo Vest Set."),
            ("Accessories and shoes", "Bow ties, pocket squares, cufflinks and oxfords to complete the position."),
            ("Next: the Queen", "Women's formal wear is being cut now. Join the waitlist on the Queen page."),
        ]), "Timeline"),
        cta("Ready to make your move?", "king.html", "Shop the collection"),
    ])

PAGES["master-tailors"] = dict(
    glyph="glyph-knight", crumb="Master Tailors", h1="Master Tailors",
    lead="The people who make the difference between a suit that hangs on you and one that was made for you.",
    meta="Meet the Checkmatela atelier — cutters, finishers and fitters in Los Angeles.",
    body=[
        section("The atelier.", '''<div class="prose">
<p>Every Checkmatela garment passes through the same small chain of hands. Patterns are drafted by a cutter, sewn and pressed by a finisher, and fitted on you by a tailor who has done this thousands of times.</p>
<p>It is a slower way to make a suit — and the only way we know to make one that lasts.</p></div>''', "Craft"),
        section("How a suit is made.", steps([
            ("Measure", "Twenty-plus measurements, taken in person at our Los Angeles studio or from our size guide for ready-to-wear."),
            ("Cut", "Cloth is laid out and cut by hand so stripes and checks meet at the seams."),
            ("Build", "Canvas, padding and lapels are shaped and stitched. This is where a jacket gets its roll."),
            ("Finish", "Buttonholes, hems and linings are finished by hand and pressed until the garment holds its line."),
            ("Fit", "One last fitting. Small adjustments — sleeve length, waist, hem — are made on the spot."),
        ]), "Process", alt=True),
        section("Who you'll meet.", cards([
            ("01", "The cutter", "Drafts the pattern and decides where every seam falls. Thinks in millimetres."),
            ("02", "The finisher", "Sews the details you'll never notice unless they were missing."),
            ("03", "The fitter", "Stands next to you at the mirror and makes the final adjustments."),
        ]), "The team"),
        cta("Meet us in person.", "book-a-fitting.html", "Book a fitting"),
    ])

PAGES["sustainability"] = dict(
    glyph="glyph-pawn", crumb="Sustainability", h1="Sustainability",
    lead="A suit worth wearing for twenty years is the most sustainable suit there is. Here is how we try to make that true.",
    meta="How Checkmatela approaches durable, repairable, responsibly made formal wear.",
    body=[
        section("Built to be kept.", '''<div class="prose">
<p>Fast fashion treats formal wear as disposable. We think the opposite: buy fewer, better pieces, take care of them and pass them down. Our approach starts with construction and cloth, not with marketing.</p></div>''', "Our approach"),
        section("Our commitments.", cards([
            ("01", "Durable by design", "Quality cloth, sturdy linings and real finishing so garments last for years, not seasons."),
            ("02", "Repair before replace", "Every order includes complimentary alterations, and we mend what we sell."),
            ("03", "Grow-with-them kids' wear", "Generous seams and quality construction so kids' suits can be altered and handed down."),
            ("04", "Less packaging", "Garment bags and boxes designed to be reused, with recyclable outer packaging."),
        ]), "Commitments", alt=True),
        section("Questions we hear.", faq([
            ("Can I have a suit repaired years later?", "Yes. Contact us and we'll advise on repair or re-fit options for any Checkmatela garment."),
            ("What happens to offcuts?", "We aim to reuse offcuts for linings, pocket squares and small accessories wherever possible."),
            ("Do you have certifications?", "Not yet. This page describes our intentions and practices, and we will publish specifics as programmes are put in place."),
        ]), "FAQ"),
        cta("Have a question about how we make things?", "mailto:" + EMAIL, "Email us"),
    ])

PAGES["press"] = dict(
    glyph="glyph-bishop", crumb="Press", h1="Press",
    lead="Writing about Checkmatela? Here is everything you need to get started.",
    meta="Checkmatela press information — brand facts, boilerplate and contact.",
    body=[
        section("About Checkmatela.", '''<div class="prose">
<p class="boiler"><strong>Checkmatela</strong> is a Los Angeles formal wear house whose collections are organised like a chessboard — King for men, Queen for women, Pawn for kids, Bishop for accessories and Rook for shoes. Each garment is named for a chess opening and designed for the moments that decide everything.</p></div>''', "Boilerplate"),
        section("Fast facts.", cards([
            ("LA", "Based in", "Los Angeles, California. Fittings by appointment."),
            ("05", "Departments", "King, Queen (opening soon), Pawn, Bishop and Rook."),
            ("10 + 34", "Openings and colourways", "Ten men's suits and tuxedos, and 34 kids' colourways across four styles."),
        ]), "At a glance", alt=True),
        section("Contact the team.", f'''<div class="prose">
<p>For interviews, imagery, samples and partnerships, email <a class="link" href="mailto:{EMAIL}">{EMAIL}</a> or call <a class="link" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p></div>''', "Press enquiries"),
        cta("Need product imagery?", "mailto:" + EMAIL + "?subject=Press%20enquiry", "Request the press kit"),
    ])

PAGES["book-a-fitting"] = dict(
    glyph="glyph-rook", crumb="Book a Fitting", h1="Book a Fitting",
    lead="A private fitting at our Los Angeles studio — measurements, fabric and fit, with someone who does this every day.",
    meta="Book a private Checkmatela fitting in Los Angeles.",
    body=[
        section("Request an appointment.", f'''<div class="fit-layout">
<form class="fit-form" data-mailto="{EMAIL}" data-subject="Fitting request — Checkmatela">
  <label>Full name<input name="Name" required autocomplete="name"></label>
  <label>Email<input type="email" name="Email" required autocomplete="email"></label>
  <label>Phone<input type="tel" name="Phone" autocomplete="tel"></label>
  <label>I'm looking for
    <select name="Looking for">
      <option>A suit</option><option>A tuxedo</option><option>A kids' suit</option><option>Accessories</option><option>Alterations</option><option>Something else</option>
    </select>
  </label>
  <label>Preferred date<input type="date" name="Preferred date"></label>
  <label>Preferred time
    <select name="Preferred time"><option>Morning</option><option>Afternoon</option><option>Evening</option></select>
  </label>
  <label class="wide">Anything we should know?<textarea name="Notes" rows="4" placeholder="Occasion, event date, sizes, questions…"></textarea></label>
  <p class="wide dialog-note">This opens a draft in your email app. Review and send it there to make an inquiry; this form does not confirm an appointment.</p>
  <button class="btn" type="submit">Draft fitting inquiry</button>
  <p class="fit-form__ok" hidden>Opening your email app with the request — press send there and we'll confirm your appointment.</p>
</form>
<aside class="fit-side">
  <h3>The studio</h3>
  <p>Los Angeles<br>Fittings by appointment</p>
  <h3>Reach us</h3>
  <p><a class="link" href="mailto:{EMAIL}">{EMAIL}</a><br><a class="link" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
  <h3>What to bring</h3>
  <p>The shoes and shirt you plan to wear, and a photo of the occasion or venue if you have one.</p>
</aside>
</div>''', "Private fittings"),
        section("What happens at a fitting.", steps([
            ("Consult", "We talk through the occasion, your style and your budget."),
            ("Measure", "Full measurements, taken by a fitter."),
            ("Try", "Try our openings on, compare cloth and colour."),
            ("Adjust", "Alterations are complimentary on every order."),
        ]), "The visit", alt=True),
    ])

PAGES["size-guide"] = dict(
    glyph="glyph-pawn", crumb="Size Guide", h1="Size Guide",
    lead="Find your Checkmatela size in a minute. When in doubt, book a fitting — alterations are on us.",
    meta="Checkmatela size guide — men's suit and trouser sizes, kids' sizes and how to measure.",
    body=[
        section("How to measure.", steps([
            ("Chest", "Measure around the fullest part of your chest, under your arms, keeping the tape level."),
            ("Waist", "Measure around your natural waistline, above the hip bone. Keep the tape snug, not tight."),
            ("Inseam", "Measure from the crotch to the floor along the inside of the leg, barefoot."),
            ("Height", "Stand straight against a wall and measure from the floor to the top of your head."),
        ]), "Before you begin"),
        section("King — men's jackets.", table(
            ["Size", "Chest (in)", "Waist (in)", "Best for height"],
            [["36", "36", "30", "5'6\" – 5'9\""], ["38", "38", "32", "5'7\" – 5'10\""], ["40", "40", "34", "5'9\" – 6'0\""],
             ["42", "42", "36", "5'10\" – 6'1\""], ["44", "44", "38", "5'11\" – 6'2\""], ["46", "46", "40", "6'0\" – 6'3\""], ["48", "48", "42", "6'0\" – 6'4\""]],
            "Jacket sizes — Short / Regular / Long lengths available by request"), "Men", alt=True),
        section("King — men's trousers.", table(
            ["Waist (in)", "28", "30", "32", "34", "36", "38", "40"],
            [["Regular inseam", "30", "31", "32", "32", "32", "32", "32"]],
            "Trouser waist and standard inseam (in) — hemmed free"), "Men"),
        section("Pawn — kids' sizes.", table(
            ["Size", "Age", "Height (in)", "Chest (in)", "Waist (in)"],
            [["2T", "2", "34–36", "20", "19"], ["4", "4", "39–41", "22", "20"], ["6", "6", "44–46", "24", "21"], ["8", "8", "49–51", "26", "22"],
             ["10", "10", "54–56", "28", "24"], ["12", "12", "58–60", "30", "26"], ["14", "14", "62–64", "32", "27"], ["16", "16", "65–67", "33", "28"]],
            "Approximate — kids grow, so if between sizes we suggest sizing up. Alterations are complimentary"), "Kids", alt=True),
        cta("Still unsure?", "book-a-fitting.html", "Book a fitting"),
    ])

PAGES["alterations"] = dict(
    glyph="glyph-bishop", crumb="Alterations", h1="Alterations",
    lead="Complimentary alterations on every order — because a great suit is one that fits you.",
    meta="Complimentary Checkmatela alterations — what's included, how it works and turnaround.",
    body=[
        section("Included with every order.", cards([
            ("01", "Hems", "Trouser and sleeve length set precisely, with hand-finished hems."),
            ("02", "Waist and fit", "Take in or let out the waist, adjust the seat and taper the leg."),
            ("03", "Jacket adjustments", "Sleeve length, shoulder tweaks and jacket length, where the construction allows."),
        ]), "What we do"),
        section("How it works.", steps([
            ("Order", "Choose your suit online or in the studio."),
            ("Fit", "Book a fitting in Los Angeles, or send us your measurements and photos if you're elsewhere."),
            ("Mark", "Our tailor marks the adjustments while you're at the mirror."),
            ("Collect", "Pick up your finished garment — typically within 5–7 days."),
        ]), "Process", alt=True),
        section("Good to know.", faq([
            ("Is there a limit?", "Standard alterations — hems, waist, sleeves — are complimentary. Major reconstruction may carry a fee, and we'll always tell you before we start."),
            ("How long does it take?", "Usually 5–7 days. Need it faster for an event? Tell us your date when you book."),
            ("Do kids' suits qualify?", "Yes, every Pawn suit includes complimentary alterations."),
            ("Can you alter things bought elsewhere?", "Ask us — email or call and we'll let you know what's possible."),
        ]), "FAQ"),
        cta("Ready to get it fitted?", "book-a-fitting.html", "Book a fitting"),
    ])

PAGES["shipping-returns"] = dict(
    glyph="glyph-rook", crumb="Shipping &amp; Returns", h1="Shipping &amp; Returns",
    lead="Free white-glove shipping over $500, and easy returns if it isn't right.",
    meta="Checkmatela shipping and returns — delivery options, timelines and how returns work.",
    body=[
        section("Shipping.", cards([
            ("01", "Free over $500", "White-glove shipping is complimentary on every order over $500."),
            ("02", "Standard delivery", "Orders under $500 ship for a flat rate, calculated at checkout."),
            ("03", "Timing", "Ready-to-wear ships within 2–3 business days. Made-to-order pieces may take longer — we'll confirm before you pay."),
        ]), "Delivery"),
        section("Returns & exchanges.", steps([
            ("Within 30 days", "Unworn garments with tags attached can be returned for a refund or exchange within 30 days of delivery."),
            ("Contact us", f"Email {EMAIL} with your order details and we'll send instructions."),
            ("Send it back", "Pack it in the original garment bag and box. Return shipping is free on exchanges."),
            ("Refund", "Refunds are issued to the original payment method within 5–10 business days of receipt."),
        ]), "Returns", alt=True),
        section("Good to know.", faq([
            ("Can altered garments be returned?", "Altered garments are made specifically for you, so they can't be returned — but we'll adjust them again until they're right."),
            ("Do you ship internationally?", "We're focused on the United States for now. Email us for other destinations."),
            ("What if it arrives damaged?", "Contact us within 48 hours with photos and we'll make it right."),
        ]), "FAQ"),
        cta("Questions about an order?", "mailto:" + EMAIL, "Email us"),
    ])


def build(slug, p):
    g = p["glyph"]
    defs = glyph_defs(sorted({g, "glyph-king"}))
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{re.sub("&amp;", "&", p["h1"])} | Checkmatela</title>
<meta name="description" content="{p["meta"]}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%230c0c0d%22/><text x=%2250%22 y=%2268%22 font-size=%2264%22 text-anchor=%22middle%22 fill=%22%23d9b876%22>&#9812;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css?v={CSS_VERSION}">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<svg width="0" height="0" style="position:absolute">
  <defs>
{defs}
  </defs>
</svg>

{ANNOUNCE}

{HEADER}
<main id="main">

<section class="cat-hero">
  <div class="cat-hero__bg"></div>
  <div class="cat-hero__fade"></div>
  <div class="cat-hero__inner">
    <div class="cat-hero__copy">
      <div class="crumbs"><a href="index.html">Home</a> <span>/</span> <span>{p["crumb"]}</span></div>
      <span class="cat-hero__glyph"><svg viewBox="0 0 100 130"><use href="#{g}" fill="currentColor"/></svg></span>
      <h1>{p["h1"]}</h1>
      <p>{p["lead"]}</p>
    </div>
    <div class="cat-hero__figures cat-hero__figures--glyph">
      <svg viewBox="0 0 100 130" aria-hidden="true"><use href="#{g}" fill="currentColor"/></svg>
    </div>
  </div>
</section>

<p class="info-preview-note">Concept content: service details and size charts are illustrative. Contact Checkmatela to confirm.</p>
{chr(10).join(p["body"])}

</main>
{FOOTER}
<script src="js/catalog.js?v={CSS_VERSION}"></script>
<script src="js/main.js?v={CSS_VERSION}"></script>
</body>
</html>
'''
    with open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", slug + ".html")


if __name__ == "__main__":
    for slug, p in PAGES.items():
        build(slug, p)
