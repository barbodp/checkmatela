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
    "men-blazers": ("men", "formal", "Blazers & Sport Coats", "Formal, velvet and linen blazers to wear with suit pants or over a dress shirt."),
    "men-suit-vests": ("men", "formal", "Suit Vests & Vest Sets", "Five- and six-button suit vests in tweed, solids and pinstripes, plus four-piece vest sets with ties."),
    "men-dress-shirts": ("men", "formal", "Dress Shirts", "Long and short sleeve dress shirts and tuxedo shirt sets."),
    "men-dress-pants": ("men", "formal", "Dress Pants", "Formal dress pants, including expandable-waist styles."),
    "men-formal-accessories": ("men", "formal", "Formal Accessories", "Cummerbund and suspender sets with matching bow ties and pocket squares."),
    "men-casual-shirts": ("men", "nsf", "Casual Shirts", "Button-down twill and casual shirts for weekends and smart-casual days."),
    "men-flannel-shirts": ("men", "nsf", "Flannel Shirts", "Soft brushed flannels for cooler days."),
    "men-polo-shirts": ("men", "nsf", "Polo Shirts", "Short sleeve striped and solid polos."),
    "men-sweaters": ("men", "nsf", "Sweaters", "Knitted cardigans, pullovers and sweaters."),
    "men-hoodies": ("men", "nsf", "Hoodies", "Everyday hoodies and sweatshirts."),
    "men-jackets": ("men", "nsf", "Jackets & Outerwear", "Bomber, cargo, fleece, sherpa-lined, reversible and rain jackets."),
    "men-leather-jackets": ("men", "nsf", "Leather Jackets", "Leather and faux leather jackets."),
    "men-activewear": ("men", "nsf", "Activewear", "Athletic shorts, joggers and track pants."),
    "men-sleepwear": ("men", "nsf", "Sleepwear", "Pajamas and loungewear."),
    "men-accessories": ("men", "nsf", "Accessories & Footwear", "Ivy caps, sandals and everyday extras."),
    "boys-suits-blazers": ("boys", "formal", "Suits & Blazers", "Slim-fit and husky suits, formal suit sets, blazer and pants sets, and velvet, corduroy and tweed blazers."),
    "boys-tuxedos": ("boys", "formal", "Tuxedos", "Shawl-lapel tuxedos in regular and husky fits."),
    "boys-suit-vests": ("boys", "formal", "Suit Vests & Vest Sets", "Suit vests, vest and pants sets, and four-piece vest sets with ties."),
    "boys-dress-shirts": ("boys", "formal", "Dress Shirts", "Dress shirts, shirt and tie sets, and tuxedo shirt sets."),
    "boys-dress-pants": ("boys", "formal", "Dress Pants", "Adjustable-waist dress pants, including husky sizes."),
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