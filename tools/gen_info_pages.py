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
    lead="The right look helps you feel ready for the moment in front of you. Checkmatela brings that idea to formal wear, one considered choice at a time.",
    meta="Meet Checkmatela, a chess-inspired formal wear concept for men, women and kids.",
    body=[
        section("A look for the moment.", '''<div class="prose"><p>Checkmatela is a formal wear concept built around a simple question: what do you need to feel ready when the occasion matters? A wedding, prom, gala or family celebration calls for more than a good-looking jacket. The style, fit and timing all have to make sense together.</p><p>Our chessboard gives the collection its character: <strong>King</strong> for men, <strong>Queen</strong> for women, <strong>Pawn</strong> for kids, <strong>Bishop</strong> for accessories and <strong>Rook</strong> for shoes. The names are playful; the decision should be easy.</p><p>The site currently previews the collection. Prices and service details are illustrative while ordering is being prepared.</p></div>''', "The idea"),
        section("How we help you choose.", cards([
            ("01", "Start with the occasion", "Choose the dress code and the person you're dressing before sorting through styles."),
            ("02", "Check the fit", "Use the measurement guide as a starting point and ask questions before committing to a size."),
            ("03", "Plan around your date", "Tell us when you need the look. Availability, delivery and any alterations must be confirmed before an order."),
        ]), "The approach", alt=True),
        cta("Have an event coming up?", "find-your-look.html", "Find your look"),
    ])

PAGES["master-tailors"] = dict(
    glyph="glyph-knight", crumb="Fit &amp; Tailoring", h1="Fit &amp; Tailoring",
    lead="A great formal look starts with measurements and a clear plan for any adjustments.",
    meta="Learn how to assess suit fit and plan alterations for a formal event.",
    body=[
        section("What a good fit looks like.", cards([
            ("01", "Shoulders", "The jacket shoulder should sit close to your natural shoulder, without a strong overhang or pull."),
            ("02", "Chest and waist", "You should be able to button the jacket comfortably. Watch for pulling across the front."),
            ("03", "Sleeves and hem", "Sleeve and trouser length shape the whole look. Bring the shoes you plan to wear when checking the hem."),
        ]), "Fit checklist"),
        section("Plan alterations early.", '''<div class="prose"><p>Hems and small waist adjustments are common; shoulders and jacket length can be more complex. Try on the full outfit well before your event and allow time for adjustments. Any Checkmatela tailoring service, cost or turnaround will be confirmed before an order is placed.</p></div>''', "Before your event", alt=True),
        cta("Need a second opinion on fit?", "book-a-fitting.html", "Ask about fit"),
    ])

PAGES["sustainability"] = dict(
    glyph="glyph-pawn", crumb="Our Approach", h1="Our Approach",
    lead="Choose pieces you can wear again, care for well and pass along when they no longer fit.",
    meta="Checkmatela's approach to long-lasting formal wear and transparent product information.",
    body=[
        section("Buy with repeat wear in mind.", '''<div class="prose"><p>A versatile color and a fit that can be adjusted make a formal outfit easier to wear beyond one event. For kids, consider how much growing room makes sense without losing the shape today.</p><p>Material sourcing, manufacturing, repair and packaging claims will be published only when they can be verified for the products sold. The current collection is a preview.</p></div>''', "Our thinking"),
        section("Questions to ask before buying.", cards([
            ("01", "Will I wear it again?", "Think about the next wedding, celebration or formal dinner, not only this one."),
            ("02", "Can it be adjusted?", "Ask which seams or hems have room for future changes."),
            ("03", "How should I care for it?", "Follow the care label for the actual garment rather than assuming all fabrics need the same treatment."),
        ]), "Useful choices", alt=True),
        cta("Questions about a piece?", "book-a-fitting.html", "Ask us"),
    ])

PAGES["press"] = dict(
    glyph="glyph-bishop", crumb="Press", h1="Press",
    lead="Information and imagery for stories about the Checkmatela concept.",
    meta="Checkmatela press information and contact details.",
    body=[
        section("About Checkmatela.", '''<div class="prose"><p><strong>Checkmatela</strong> is a chess-inspired formal wear concept organized into five departments: King for men, Queen for women, Pawn for kids, Bishop for accessories and Rook for shoes. The website previews looks for weddings, galas and other meaningful occasions. Online ordering and service terms are in development.</p></div>''', "Boilerplate"),
        section("Contact.", f'''<div class="prose"><p>For interviews, imagery or partnerships, email <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>.</p></div>''', "Press enquiries", alt=True),
    ])

PAGES["book-a-fitting"] = dict(
    glyph="glyph-rook", crumb="Ask About Fit", h1="Ask About Fit",
    lead="Tell us who you're dressing, what the occasion is and when it happens. We can discuss the look and what needs confirming before you buy.",
    meta="Contact Checkmatela about formal wear fit, event dates and product availability.",
    body=[
        section("Start a conversation.", f'''<div class="fit-layout">
<form class="fit-form" data-mailto="{EMAIL}" data-subject="Event and fit enquiry — Checkmatela">
  <label>Full name<input name="Name" required autocomplete="name"></label>
  <label>Email<input type="email" name="Email" required autocomplete="email"></label>
  <label>Phone<input type="tel" name="Phone" autocomplete="tel"></label>
  <label>I'm looking for
    <select name="Looking for"><option>A men's suit</option><option>A tuxedo</option><option>A kids' look</option><option>The Queen collection</option><option>Accessories or shoes</option><option>Fit or alterations advice</option><option>Something else</option></select>
  </label>
  <label>Event date<input type="date" name="Event date"></label>
  <label>Occasion
    <select name="Occasion"><option>Wedding</option><option>Black tie or gala</option><option>Prom or school event</option><option>Family celebration</option><option>Business or other</option></select>
  </label>
  <label class="wide">What would help you decide?<textarea name="Notes" rows="4" placeholder="Style, size, dress code, location or timing questions…"></textarea></label>
  <button class="btn" type="submit">Open email draft</button>
  <p class="fit-form__ok" hidden>Your email app is opening. Please send the draft to submit your enquiry.</p>
</form>
<aside class="fit-side"><h3>Before you send</h3><p>This form opens an email draft on your device. Your enquiry is sent only after you press Send in your email app.</p><h3>Fit planning</h3><p>Have your measurements, event date and dress code handy. If you're checking trouser length, measure with the shoes you'll wear.</p><h3>Reach us directly</h3><p><a class="link" href="mailto:{EMAIL}">{EMAIL}</a></p></aside>
</div>''', "Fit and event help"),
        section("A useful order of moves.", steps([
            ("Choose the occasion", "Start with the dress code, venue and who you're dressing."),
            ("Check measurements", "Use the size chart as an estimate; product measurements still need confirmation."),
            ("Confirm the timeline", "Ask about stock, delivery, returns and tailoring before relying on an arrival date."),
        ]), "Before you buy", alt=True),
    ])

PAGES["size-guide"] = dict(
    glyph="glyph-pawn", crumb="Size Guide", h1="Size Guide",
    lead="Measure first, compare second. These charts are planning references until product-specific measurements are confirmed.",
    meta="Illustrative men's and kids' formal wear size charts and a practical measurement guide.",
    body=[
        section("How to measure.", steps([
            ("Chest", "Measure around the fullest part of the chest, under the arms, keeping the tape level."),
            ("Waist", "Measure around the natural waist. Keep the tape comfortable, not tight."),
            ("Inseam", "Measure from crotch to the desired trouser hem while wearing the planned shoes."),
            ("Height", "Stand straight against a wall and measure from floor to the top of the head."),
        ]), "Before you begin"),
        section("King — men's jackets.", table(
            ["Illustrative size", "Chest (in)", "Waist (in)", "Height reference"],
            [["36", "36", "30", "5'6\" – 5'9\""], ["38", "38", "32", "5'7\" – 5'10\""], ["40", "40", "34", "5'9\" – 6'0\""], ["42", "42", "36", "5'10\" – 6'1\""], ["44", "44", "38", "5'11\" – 6'2\""], ["46", "46", "40", "6'0\" – 6'3\""], ["48", "48", "42", "6'0\" – 6'4\""]],
            "Planning reference only — garment measurements and available lengths must be confirmed"), "Men", alt=True),
        section("Pawn — kids' sizes.", table(
            ["Illustrative size", "Age reference", "Height (in)", "Chest (in)", "Waist (in)"],
            [["2T", "2", "34–36", "20", "19"], ["4", "4", "39–41", "22", "20"], ["6", "6", "44–46", "24", "21"], ["8", "8", "49–51", "26", "22"], ["10", "10", "54–56", "28", "24"], ["12", "12", "58–60", "30", "26"], ["14", "14", "62–64", "32", "27"], ["16", "16", "65–67", "33", "28"]],
            "Age is a starting point; compare actual measurements and confirm the garment dimensions"), "Kids"),
        section("Before choosing a size.", '''<div class="prose"><p>If someone falls between sizes, compare the chest and waist first and ask about the specific garment. Allow enough time for a try-on and any alterations. These illustrative charts should not be treated as a fit guarantee.</p></div>''', "Fit confidence", alt=True),
        cta("Still unsure about fit?", "book-a-fitting.html", "Ask a fit question"),
    ])

PAGES["alterations"] = dict(
    glyph="glyph-bishop", crumb="Alterations", h1="Alterations",
    lead="Plan the final fit before the event. Alteration options, prices and turnaround are confirmed case by case.",
    meta="Practical formal wear alterations guidance and Checkmatela service status.",
    body=[
        section("What can often be adjusted.", cards([
            ("01", "Trousers", "Hem length and small waist changes are common. Bring the shoes you plan to wear."),
            ("02", "Sleeves", "Sleeve length may be adjustable depending on cuff construction and button placement."),
            ("03", "Jacket fit", "Waist shaping is often possible; shoulder and jacket length changes can be more involved."),
        ]), "Fit planning"),
        section("Allow a buffer.", '''<div class="prose"><p>Try on the complete outfit with enough time for a tailor to assess it and make adjustments. Do not assume a particular garment can be altered until a professional has seen its construction. Checkmatela has not published a complimentary alteration policy or guaranteed turnaround for this preview collection.</p></div>''', "Before the event", alt=True),
        cta("Have a fit or timing question?", "book-a-fitting.html", "Ask about fit"),
    ])

PAGES["shipping-returns"] = dict(
    glyph="glyph-rook", crumb="Shipping &amp; Returns", h1="Shipping &amp; Returns",
    lead="Have an event date? Check availability, delivery timing and return terms before you commit to a look.",
    meta="Checkmatela delivery and returns status for the preview collection.",
    body=[
        section("Current status.", '''<div class="prose"><p>The Checkmatela collection is a website preview. Online checkout is not connected, so orders, delivery dates and returns are not yet available through this site. Displayed prices and shipping estimates are illustrative.</p><p>Before ordering begins, this page will show the actual service areas, shipping rates, cutoff times, exchange and refund windows, and any exceptions for altered or special-order pieces.</p></div>''', "Before you order"),
        section("Questions to settle for an event.", steps([
            ("Confirm stock", "Check that the chosen style, color and size are available."),
            ("Confirm delivery", "Work backward from your event and leave time for a try-on and possible alterations."),
            ("Know your options", "Review the final exchange, return and alteration terms for the exact item before payment."),
        ]), "Event planning", alt=True),
        cta("Need help planning around a date?", "book-a-fitting.html", "Ask about timing"),
    ])

PAGES["find-your-look"] = dict(
    glyph="glyph-king", crumb="Fit & Timing Check", h1="Find your look. Plan the fit.",
    lead="A quick check for your occasion, measurements and event date — so you know what to confirm before choosing a look.",
    meta="Check formal wear style, fit planning and event timing with Checkmatela.",
    body=[
        section("Start with fit and timing.", '''<form class="look-finder" id="lookFinder">
<label>Who are you dressing?<select name="wearer"><option value="men">Men</option><option value="kids">Kids</option><option value="women">Women</option></select></label>
<label>What's the occasion?<select name="occasion"><option value="wedding">Wedding</option><option value="black-tie">Black tie or gala</option><option value="prom">Prom or school event</option><option value="family">Family celebration</option><option value="business">Business or other</option></select></label>
<label>When is the event?<input type="date" name="eventDate"></label>
<fieldset class="look-finder__measurements"><legend>Fit basics <small>(optional)</small></legend><p>Enter body measurements in inches if you have them. They stay on this page.</p><div>
<label>Chest (inches)<input type="number" name="chest" inputmode="decimal" min="18" max="70" step="0.5" placeholder="e.g. 40"></label>
<label>Waist (inches)<input type="number" name="waist" inputmode="decimal" min="18" max="70" step="0.5" placeholder="e.g. 34"></label>
</div></fieldset>
<button class="btn" type="submit">See my fit &amp; timing plan</button>
</form><div class="look-result" id="lookResult" role="status" aria-live="polite" hidden></div>
<p class="look-note">This check suggests a style and planning steps. It cannot confirm stock, exact fit or delivery. Online ordering is not connected.</p>''', "Your quick check"),
        section("Before you decide.", steps([
            ("Choose the dress code", "Black tie usually points toward a tuxedo. Weddings and family events allow more flexibility."),
            ("Check fit", "Measure chest, waist, height and inseam, then compare with the guide and ask about the garment."),
            ("Check your date", "Build in time to try on the complete look and adjust it if needed."),
        ]), "Fit and timing", alt=True),
        cta("Need help with a specific look or date?", "book-a-fitting.html", "Ask about fit & timing"),
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

<section class="cat-hero">
  <div class="cat-hero__bg"></div>
  <div class="cat-hero__fade"></div>
  <div class="cat-hero__inner">
    <div class="cat-hero__copy">
      <div class="crumbs"><a href="index.html">Home</a> <span>/</span> <span>{p["crumb"]}</span></div>
      <span class="cat-hero__glyph"><svg viewBox="0 0 100 100"><use href="#{g}" fill="currentColor"/></svg></span>
      <h1>{p["h1"]}</h1>
      <p>{p["lead"]}</p>
    </div>
    <div class="cat-hero__figures cat-hero__figures--glyph">
      <svg viewBox="0 0 100 130" aria-hidden="true"><use href="#{g}" fill="currentColor"/></svg>
    </div>
  </div>
</section>

{chr(10).join(p["body"])}

{FOOTER.replace("</body>", '<script src="js/look-finder.js"></script></body>') if slug == "find-your-look" else FOOTER}
'''
    with open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", slug + ".html")


STATES = "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()


def build_checkout():
    """checkout.html — the pre-checkout: bag review, contact/delivery form with inline validation, shipping method, payment PREVIEW
    (no card details are collected; nothing is sent anywhere), order summary and a confirmation preview. Logic in js/checkout.js."""
    defs = glyph_defs(["glyph-king"])
    states = "".join(f'<option value="{x}">{x}</option>' for x in STATES)
    def field(name, label, extra="", typ="text", auto="", req=True, wide=False, hint=""):
        return (f'<div class="co-field{" co-wide" if wide else ""}"><label for="f-{name}">{label}{"" if req else " <em>(optional)</em>"}</label>'
                f'<input id="f-{name}" name="{name}" type="{typ}" autocomplete="{auto}" {"required" if req else ""} {extra}>'
                f'<small class="co-err" id="e-{name}" role="alert"></small>{f"<small class=co-hint>{hint}</small>" if hint else ""}</div>')
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Checkout (preview) | Checkmatela</title>
<meta name="robots" content="noindex">
<meta name="description" content="Checkmatela checkout preview — review your bag, delivery and shipping options.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%230c0c0d%22/><text x=%2250%22 y=%2268%22 font-size=%2264%22 text-anchor=%22middle%22 fill=%22%23d9b876%22>&#9812;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css?v={CSS_VERSION}">
</head>
<body class="checkout-page">

<svg width="0" height="0" style="position:absolute">
  <defs>
{defs}
  </defs>
</svg>

{ANNOUNCE}

{HEADER}

<main class="co" id="main">
  <div class="container">
    <div class="co-top">
      <div>
        <span class="eyebrow">Checkout</span>
        <h1>Review your preview bag</h1>
      </div>
      <ol class="co-steps" aria-label="Checkout steps">
        <li class="is-done"><a href="index.html">Shop</a></li><li class="is-on">Details</li><li>Payment</li><li>Confirmation</li>
      </ol>
    </div>

    <p class="co-banner" role="note"><b>Preview only.</b> This site cannot take orders yet. Prices, shipping and taxes are examples. No payment is collected and your details are not sent or saved. <a href="book-a-fitting.html">Ask about a look or your event date →</a></p>

    <section class="co-empty" hidden>
      <h2>Your bag is empty</h2>
      <p>Add a piece to see the checkout preview.</p>
      <p><a class="btn" href="king.html">Shop King</a> <a class="btn dark-ghost" href="pawn.html">Shop Pawn</a></p>
    </section>

    <div class="co-grid">
      <form class="co-form" id="coForm" novalidate>
        <section class="co-card">
          <h2><span>1</span> Contact</h2>
          {field("email", "Email", 'inputmode="email" placeholder="you@example.com"', "email", "email")}
          {field("phone", "Phone", 'inputmode="tel" placeholder="(310) 555-0123"', "tel", "tel", req=False, hint="Preview field only; this information is not sent.")}
        </section>

        <section class="co-card">
          <h2><span>2</span> Delivery</h2>
          <div class="co-row">
            {field("first", "First name", "", "text", "given-name")}
            {field("last", "Last name", "", "text", "family-name")}
          </div>
          {field("address", "Address", 'placeholder="Street address"', "text", "address-line1", wide=True)}
          {field("apt", "Apartment, suite, etc.", "", "text", "address-line2", req=False, wide=True)}
          <div class="co-row co-row--3">
            {field("city", "City", "", "text", "address-level2")}
            <div class="co-field"><label for="f-state">State</label><select id="f-state" name="state" autocomplete="address-level1" required><option value="">State</option>{states}</select><small class="co-err" id="e-state" role="alert"></small></div>
            {field("zip", "ZIP code", 'inputmode="numeric" maxlength="10" placeholder="90015"', "text", "postal-code")}
          </div>
          <p class="co-hint">This is an example address form. Shipping areas are not confirmed.</p>
        </section>

        <section class="co-card">
          <h2><span>3</span> Shipping method</h2>
          <div class="co-options" id="shipOptions" role="radiogroup" aria-label="Shipping method"></div>
        </section>

        <section class="co-card">
          <h2><span>4</span> Payment</h2>
          <div class="co-options" role="radiogroup" aria-label="Payment method">
            <label class="co-opt"><input type="radio" name="pay" value="card" checked><span><b>Credit or debit card</b><small>Card fields appear here once payments are connected.</small></span></label>
            <label class="co-opt"><input type="radio" name="pay" value="apple"><span><b>Apple Pay</b><small>Example option; availability to be confirmed.</small></span></label>
            <label class="co-opt"><input type="radio" name="pay" value="paypal"><span><b>PayPal</b><small>Example option; availability to be confirmed.</small></span></label>
          </div>
          <p class="co-note">Payments aren't connected in this preview. <b>No card details are asked for or stored.</b></p>
        </section>

        <div class="co-actions">
          <button class="btn co-place" type="submit">Place order (preview)</button>
          <a class="link" href="#" id="editBag">Edit bag</a>
        </div>
        <p class="co-error-summary" id="coSummary" role="alert" hidden></p>
      </form>

      <aside class="co-summary" aria-label="Order summary">
        <h2>Order summary</h2>
        <ul class="co-items" id="coItems"></ul>
        <form class="co-promo" id="promoForm" novalidate>
          <label for="promo" class="visually-hidden">Promo code</label>
          <input id="promo" name="promo" placeholder="Promo code" autocomplete="off" spellcheck="false">
          <button type="submit" class="btn small dark-ghost">Apply</button>
        </form>
        <p class="co-promo-msg" id="promoMsg" role="status"></p>
        <dl class="co-totals">
          <div><dt>Subtotal</dt><dd id="tSub">$0</dd></div>
          <div class="co-disc" hidden><dt>Discount</dt><dd id="tDisc">−$0</dd></div>
          <div><dt>Shipping</dt><dd id="tShip">—</dd></div>
          <div><dt>Estimated tax</dt><dd id="tTax">$0</dd></div>
          <div class="co-total"><dt>Total</dt><dd id="tTotal">$0</dd></div>
        </dl>
        <p class="co-fine">Prices, shipping rates and taxes are illustrative placeholders. No delivery offer is active. <a href="shipping-returns.html">Read the current service status</a>.</p>
      </aside>
    </div>

    <section class="co-done" id="coDone" hidden aria-live="polite"></section>
  </div>
</main>

{FOOTER.replace('<script src="js/cart.js"></script>', '<script src="js/cart.js"></script>' + chr(10) + '<script src="js/checkout.js?v=2"></script>')}
'''
    with open(os.path.join(ROOT, "checkout.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote checkout.html")


if __name__ == "__main__":
    for slug, p in PAGES.items():
        build(slug, p)
    build_checkout()
