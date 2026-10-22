"""The site's Men / Kids categories (all brands), shared by tools/gb_fetch.py (photo archive folders) and tools/gen_gioberti.py (pages, menus).
men-suits, men-tuxedos and boys-tuxedos only hold other brands' pieces (Antonio Uomo, Magen Kids) for now.

Every Gioberti product is filed under one of our categories by its Gioberti product type (TYPE_MAP), then corrected by its title (TITLE_RULES) where Gioberti's own type is misleading, e.g. a sweater filed
as outerwear. The rules are generic, so new products are filed the same way.
"""
import re

# category key -> (department, group, label, one-line description). Order = order in menus, pills and landing pages.
CATS = {
    "men-suits": ("men", "formal", "Suits", "Two- and three-piece suits in slim and classic fits: solids, plaids and textured fabrics."),
    "men-tuxedos": ("men", "formal", "Tuxedos", "Two- and three-piece tuxedos for black tie, prom and weddings."),
    "men-blazers": ("men", "formal", "Blazers & Sport Coats", "Formal, velvet, linen and shiny patterned jackets to wear with suit pants or over a dress shirt."),
    "men-suit-vests": ("men", "formal", "Suit Vests & Vest Sets", "Five- and six-button suit vests in tweed, solids and pinstripes, plus four-piece vest sets with ties."),
    "men-dress-shirts": ("men", "formal", "Dress Shirts", "Long and short sleeve dress shirts and tuxedo shirt sets."),
    "men-dress-pants": ("men", "formal", "Dress Pants", "Slim-fit stretch dress pants and expandable-waist styles."),
    "men-formal-accessories": ("men", "formal", "Formal Accessories", "Cummerbund and suspender sets with matching bow ties and pocket squares."),
    "men-casual-shirts": ("men", "nsf", "Casual Shirts", "Button-down twill and casual shirts for weekends and smart-casual days."),
    "men-flannel-shirts": ("men", "nsf", "Flannel Shirts", "Soft brushed flannels for cooler days."),
    "men-polo-shirts": ("men", "nsf", "Polo Shirts", "Short sleeve striped polos, from fine pinstripes to bold bars."),
    "men-sweaters": ("men", "nsf", "Sweaters", "Knitted cardigans, pullovers and sweaters."),
    "men-hoodies": ("men", "nsf", "Hoodies", "Everyday hoodies and sweatshirts."),
    "men-jackets": ("men", "nsf", "Jackets & Outerwear", "Bomber, cargo, fleece, sherpa-lined, reversible and rain jackets."),
    "men-leather-jackets": ("men", "nsf", "Leather Jackets", "Leather and faux leather jackets."),
    "men-activewear": ("men", "nsf", "Activewear", "Athletic shorts, joggers and track pants."),
    "men-sleepwear": ("men", "nsf", "Sleepwear", "Pajamas and loungewear."),
    "men-accessories": ("men", "nsf", "Accessories & Footwear", "Ivy caps, sandals and everyday extras."),
    "boys-suits-blazers": ("boys", "formal", "Suits & Blazers", "Slim-fit and husky suits, formal suit sets, blazer and pants sets, and velvet, corduroy and tweed blazers."),
    "boys-tuxedos": ("boys", "formal", "Tuxedos", "Shawl-lapel tuxedos in regular and husky fits."),
    "boys-suit-vests": ("boys", "formal", "Suit Vests & Vest Sets", "Suit vests, suit and tuxedo vest sets, vest and pants sets, and four-piece vest sets with ties."),
    "boys-dress-shirts": ("boys", "formal", "Dress Shirts", "Dress shirts, shirt and tie sets, and tuxedo shirt sets."),
    "boys-dress-pants": ("boys", "formal", "Dress Pants", "Dress pants in regular and husky fits, from adjustable-waist styles to classic flat fronts."),
    "boys-formal-accessories": ("boys", "formal", "Formal Accessories", "Cummerbund and suspender sets with matching bow ties and pocket squares."),
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
    "Mens Hoodies": "men-hoodies", "Mens Jackets": "men-jackets", "Mens Outerwear": "men-jackets", "Mens Leather Jacket": "men-leather-jackets",
    "Mens Active Wear": "men-activewear", "Mens": "men-activewear", "Mens Sleepwear": "men-sleepwear", "Mens Accessories": "men-accessories",
    "Boys Blazers": "boys-suits-blazers", "Boys Suit Vest": "boys-suit-vests", "Boys Dress Shirts": "boys-dress-shirts", "Boys Dress Pants": "boys-dress-pants",
    "Boys Button Down Shirts": "boys-casual-shirts", "Boys Polos and T-Shirts": "boys-polo-shirts", "Boys Sweaters": "boys-sweaters", "Boys Jackets": "boys-jackets",
    "Boys Active Wear": "boys-activewear", "Boys Shorts": "boys-shorts", "Boys Sleepwear": "boys-sleepwear", "Boys Accessories": "boys-accessories",
}
FORMAL_ACCESSORIES = ("men-formal-accessories", "boys-formal-accessories")    # also shown on the Accessories page (bishop.html), men's and boys' apart


# (title pattern, title must NOT match, the categories it applies to, the category it goes to) - first match wins
TITLE_RULES = [
    (r"\bsweaters?\b|cardigan", r"hoodie", {"men-jackets", "men-hoodies"}, "men-sweaters"),            # "Men's Super Soft Sweater" (outerwear), "Knitted Sweater w/ Sherpa" (hoodies)
    (r"\bhoodie\b", r"jacket|flannel|shirt|sweater", {"men-jackets"}, "men-hoodies"),                   # "Men's Polar Fleece Hoodie" (outerwear)
    (r"\bsweaters?\b|cardigan", r"hoodie", {"boys-jackets"}, "boys-sweaters"),
    (r"\bhoodie\b", r"jacket|flannel|shirt|sweater", {"boys-jackets"}, "boys-sweaters"),
]


def category_of(handle, ptype, title=""):
    if re.search(r"cumberbund|cummerbund|suspender", handle):
        return "boys-formal-accessories" if re.match(r"(cm-8|susk)", handle) else "men-formal-accessories"
    if handle.startswith("si-501"):        # filed by Gioberti under dress shirts, but they are casual twill shirts
        return "men-casual-shirts"
    cat = TYPE_MAP.get(ptype)
    for pat, unless, scope, to in TITLE_RULES:
        if cat in scope and re.search(pat, title, re.I) and not re.search(unless, title, re.I):
            return to
    return cat


def dept_of(handle, cat):
    return CATS[cat][0] if cat else None


def folder_label(handle, cat):
    """Photo archive folder for a category: 'Men - Casual Shirts', 'Boys - Formal Accessories'…"""
    return f"{'Men' if dept_of(handle, cat) == 'men' else 'Boys'} - {CATS[cat][2]}"

# ---------------------------------------------------------------- curated, combined listings (user, 2026-10-22)
# Gioberti sells the same shirt as several listings (sometimes two for one style) with dozens of near-identical plaids. Each entry below
# becomes ONE product page built from its source listings, showing only the plaids listed (Gioberti fabric number -> display name),
# picked for stock depth, fabrics Gioberti makes in several styles (its core fabrics), its best-seller order and one of each colour story.
# solids=True keeps every solid colour of the sources (user: solids are never cut). colours=None keeps every colour.
# A colours key is either a Gioberti fabric number (plaids: the number is kept in the colour name) or an exact Gioberti colour name (polos).
# Short and long sleeve stay separate listings (user). The stock sync keeps these colours' stock current; colours not listed here never come
# back on their own — edit this list to change the range. retired: earlier combined pages that now redirect here.
CURATED = [
    # Men's casual shirts
    dict(handle="mens-plaid-short-sleeve-shirt", name="Men's Plaid Short Sleeve Shirt", code="SS-92", retired=["mens-plaid-shirt"],
         sources=["ss-92-mens-casual-plaid-short-sleeve-button-down-dress-shirt", "ss-92-special-mens-plaid-short-sleeve-shirt"],
         colours={"1049": "Red / Black / Gray", "632": "Black / White", "1055": "Red / Navy / White", "1053": "Blue / Navy / White", "727": "Khaki / Navy",
                  "1090": "Blue / Grey / Black", "1018": "Navy / White", "1164": "Green / White", "1163": "Royal / White", "1096": "Teal / Brown / White"}),
    dict(handle="mens-plaid-long-sleeve-shirt", name="Men's Plaid Long Sleeve Shirt", code="LS-92",
         sources=["ls-92-gioberti-plaid-long-sleeve-shirt"],
         colours={"1049": "Red / Black / Gray", "632": "Black / White", "1055": "Red / Navy / White", "1053": "Blue / Navy / White", "727": "Khaki / Navy",
                  "1090": "Blue / Grey / Black", "1018": "Navy / White", "1154": "Cobalt / Peach / White", "777": "Turquoise", "1086": "Teal / Brown",
                  "211": "Light Blue / Yellow / White"}),
    dict(handle="mens-plaid-pearl-snap-short-sleeve-shirt", name="Men's Plaid Pearl Snap Short Sleeve Shirt", code="SS-92W", retired=["mens-plaid-pearl-snap-western-shirt"],
         sources=["ss-92w-mens-plaid-western-short-sleeve-shirt", "ss-92w-special-mens-plaid-western-short-sleeve-shirt"],
         colours={"727": "Khaki / Navy", "978": "Black / White / Gray", "1103": "Red / Navy / Yellow", "1049": "Red / Black / Gray", "1036": "Red / Navy / White",
                  "1053": "Blue / Navy / White", "995": "Blue / Khaki / White", "1061": "Orange / White / Navy", "1060": "Blue Checkered", "1059": "Green / White"}),
    dict(handle="mens-plaid-pearl-snap-long-sleeve-shirt", name="Men's Plaid Pearl Snap Long Sleeve Shirt", code="LS-92W",
         sources=["ls-92w-gioberti-western-plaid-long-sleeve-shirt"],
         colours={"727": "Khaki / Navy", "978": "Black / White / Gray", "1103": "Red / Navy / Yellow", "1049": "Red / Black / Gray", "1036": "Red / Navy / White",
                  "1053": "Blue / Navy / White", "777": "Turquoise", "26": "Brown / Yellow / Turquoise", "1154": "Cobalt / Peach / White",
                  "124": "Red / Black / Orange", "6": "Sage / Olive / Khaki", "252": "Charcoal / Orange / White"}),
    dict(handle="mens-solid-pearl-snap-short-sleeve-shirt", name="Men's Solid Pearl Snap Short Sleeve Shirt", code="SS-95W", retired=["mens-solid-pearl-snap-western-shirt"],
         sources=["ss-95w-mens-casual-western-solid-short-sleeve-shirt-with-pearl-snaps"], colours=None),
    dict(handle="mens-solid-pearl-snap-long-sleeve-shirt", name="Men's Solid Pearl Snap Long Sleeve Shirt", code="LS-95W",
         sources=["ls-95w-mens-solid-long-sleeve-western-shirt"], colours=None),
    # Men's flannel shirts (all long sleeve)
    dict(handle="mens-plaid-flannel-shirt", name="Men's Plaid Flannel Shirt", code="LS-92F", solids=True,
         sources=["ls-92f-mens-long-sleeve-plaid-checkered-flannel", "ls-92f-special-mens-long-sleeve-plaid-checkered-flannel"],
         colours={"86": "Black / Charcoal", "48": "Red / Black", "78": "Orange / Khaki / Teal", "98": "Charcoal / Red", "35": "Black / White / Red",
                  "99": "Black / White", "89": "Green / Black / Royal Blue", "79": "Black / Blue Check", "1135": "Gray / Navy / White",
                  "85": "Red / Navy / Gray", "727": "Khaki / Navy", "971": "Navy / Orange"}),
    dict(handle="mens-hooded-flannel-shirt", name="Men's Removable Hoodie Flannel Shirt", code="LS-92H", solids=True,
         sources=["ls-92h-mens-hooded-long-sleeve-plaid-flannel", "ls-92h-special-mens-hooded-long-sleeve-plaid-flannel"],
         colours={"86": "Black / Charcoal / Gray", "9": "Charcoal / Red", "1139": "Blue / Gray / Black", "99": "Black / White", "89": "Black / Green / Royal Blue",
                  "51": "Khaki / Umber", "48": "Red / Black Check", "12": "Blue / Gold", "1135": "Gray / Navy / White", "79": "Royal / Black Check"}),
    dict(handle="mens-flannel-shirt-with-snaps", name="Men's Flannel Shirt w/ Snaps", code="LS-92FS", solids=True,
         sources=["ls-92fs-mens-long-sleeve-flannel-shirt-with-snap-button"],
         colours={"86": "Charcoal / Gray / Black", "48": "Red / Black Check", "78": "Orange / Khaki / Teal", "35": "Black / White / Red", "971": "Navy / Orange",
                  "727": "Khaki / Navy", "1151": "Navy / Brown / Magenta", "1139": "Blue / Gray / Black", "774": "Dark Green / Black", "1166": "Blue / Red / White"}),
    dict(handle="mens-flannel-shirt-with-corduroy-contrast", name="Men's Flannel Shirt w/ Corduroy Contrast", code="LS-94FC", solids=True,
         sources=["ls-94fc-mens-long-sleeve-flannel-shirt"],
         colours={"78": "Orange / Khaki / Teal", "48": "Black / Red Check", "1139": "Blue / Gray / Black", "56": "Dark Blue / Gray",
                  "1146": "Royal Blue / Midnight / Yellow", "97": "Gray / Black", "54": "Dark Green / Red", "1116": "Black / Gray / Coral",
                  "1117": "Brown / Khaki", "1079": "Aqua / Turquoise / Orange"}),
    # Men's polo shirts: all striped designs (no solids). The 9 strongest designs (Gioberti best-seller order, stock), each with a name that says
    # which stripe it is (Gioberti calls most of them "Jersey Polo" / "Striped Polo"); duplicate colours (Charcoal A/B/C, logo copies…) and colours with no stock cut.
    dict(handle="mens-gradient-stripe-polo", name="Men's Gradient Stripe Polo w/ Pocket", code="PS-931", sources=["ps-931-mens-stripe-polo-shirt-with-pockets"],
         colours={"Blue": "Blue", "Cobalt": "Cobalt", "Red": "Red", "Khaki": "Khaki", "Camel": "Camel", "Brown": "Brown", "Olive": "Olive", "Green": "Green",
                  "Charcoal C": "Charcoal", "White": "White"}),
    dict(handle="mens-fine-stripe-polo", name="Men's Fine Stripe Polo w/ Pocket", code="PS-942", sources=["ps-942-mens-stripe-polo-shirt-with-pockets"], colours=None),
    dict(handle="mens-chest-stripe-polo", name="Men's Chest Stripe Polo", code="PS-9327", sources=["ps-9327-mens-striped-polo-shirt-with-pocket"],
         colours={"Black B": "Black", "Gray": "Gray", "Hunter Green": "Hunter Green", "NavyB": "Navy", "White B": "White"}),
    dict(handle="mens-heather-stripe-polo", name="Men's Heather Stripe Polo", code="PS-943", sources=["ps-943-mens-stripe-polo-shirt"],
         colours={"Brown": "Brown", "Blue": "Blue", "Gray": "Gray", "Hunter": "Hunter Green", "Navy": "Navy"}),
    dict(handle="mens-accent-stripe-polo", name="Men's Accent Stripe Polo", code="PS-934", sources=["ps-934-mens-stripe-polo-shirt"], colours=None),
    dict(handle="mens-multi-stripe-polo", name="Men's Multi-Stripe Polo", code="PS-947", sources=["ps-947-mens-stripe-polo-shirt"],
         colours={"Burgundy - Style 947": "Burgundy", "Camel - Style 947": "Camel", "Charcoal - Style 947": "Charcoal"}),
    dict(handle="mens-pin-stripe-polo", name="Men's Pin Stripe Polo", code="PS-945", sources=["ps-945-mens-stripe-polo-shirt"],
         colours={"Hunter Green - Style 945": "Hunter Green", "Red - Style 945": "Red", "Brown - Style 945": "Brown"}),
    dict(handle="mens-jersey-stripe-polo", name="Men's Jersey Stripe Polo", code="PS-937",
         sources=["ps-937-mens-striped-short-jersey-sleeve-polo-shirt", "ps-937-mens-striped-short-jersey-sleeve-polo-shirt-pocket"],
         colours={"Black B": "Black", "White C": "White", "Royal Blue": "Royal Blue (with pocket)"}),
    dict(handle="mens-bold-stripe-polo", name="Men's Bold Stripe Polo w/ Pocket", code="PS-933", sources=["ps-933-mens-stripe-polo-shirt-with-pockets"],
         colours={"Black A - Style 933": "Black / Red", "Black B - Style 933": "Black / Blue", "Charcoal - Style 933": "Charcoal / Blue", "Royal Blue - Style 933": "Royal Blue / Black"}),
    # Boys' polo: Gioberti's PS-851XP listing mixes three yacht-club designs with the same colours; one of each colour, the version with most stock.
    dict(handle="boys-yacht-club-pique-polo", name="Boy's Yacht Club Pique Polo", code="PS-851XP", sources=["ps-851xp-kids-yacht-club-pique-polo-shirt"],
         colours={"Black- 8510P": "Black", "Navy- 8511P": "Navy", "White- 8510P": "White", "Aqua- 8512P": "Aqua", "Gray- 8511P": "Gray",
                  "Red- 8511P": "Red", "Royal Blue- 8511P": "Royal Blue"}),
]

# Gioberti listings left off the site on purpose (user, 2026-10-22: "highest chance of selling", no repetition). Their old pages redirect to their category.
HIDDEN = {
    "ps-9-mens-striped-polo-shirt": "three different styles in one listing, low seller",
    "ps-939-mens-striped-polo-shirt": "low seller",
    "ps-946-mens-stripe-polo-shirt": "low seller",
    "ps-9323-mens-striped-polo-shirt": "low seller, logo / no-logo duplicate colours",
    "ps-9328-mens-striped-polo-shirt-with-pocket": "lowest seller",
    "ps-944-mens-stripe-polo-shirt": "most colours out of stock",
    "ps-9306-mens-stripe-polo-shirt-with-pockets": "near-duplicate of the Bold Stripe Polo",
}
