"""Builds the King product grid (filters, sorting, compare, quick view) in king.html from tools/catalog/king.json.

Run:  python3 tools/gen_king_page.py     (then tools/gen_home_showcase.py so the homepage carousel matches)
"""
import os, json, html
from shoplib import shop_block, replace_between, esc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARROW_NONE = ""

FACETS = [
    {"key": "color", "label": "Colour", "swatch": True},
    {"key": "style", "label": "Style"},
    {"key": "pattern", "label": "Pattern"},
    {"key": "occasion", "label": "Occasion"},
]
REVIEW_FACETS = [["height", "Height"], ["build", "Build"], ["size", "Size bought"], ["fit", "Fit"], ["occasion", "Occasion"]]


def card(p):
    occ = "|".join(p["occasion"]) if isinstance(p["occasion"], list) else p["occasion"]
    img = f"assets/img/products/{p['slug']}.jpg"
    return f'''            <div class="product-card" data-id="king/{p["slug"]}" data-name="{esc(p["name"])}" data-tag="{esc(p["tag"])}" data-price="{p["price"]}" data-img="{img}" data-f-color="{esc(p["color"])}" data-f-style="{esc(p["style"])}" data-f-pattern="{esc(p["pattern"])}" data-f-occasion="{esc(occ)}">
              <div class="product-card__frame">
                <img src="{img}" alt="{esc(p["alt"])}" loading="lazy">
                <span class="product-card__notation">{esc(p["notation"])}</span>
                <button type="button" class="cmp-toggle" aria-pressed="false">+ Compare</button>
                <button type="button" class="product-card__quick"><span class="btn small">Quick View &amp; Reviews</span></button>
              </div>
              <div class="product-card__meta"><div><h4>{esc(p["name"])}</h4><span class="piece-tag">{esc(p["tag"])}</span></div><span class="product-card__price">${p["price"]}</span></div>
            </div>'''


def main():
    cat = json.load(open(os.path.join(ROOT, "tools", "catalog", "king.json"), encoding="utf-8"))["products"]
    block = shop_block("\n".join(card(p) for p in cat), FACETS, "king", count_noun="openings", review_facets=REVIEW_FACETS)
    path = os.path.join(ROOT, "king.html")
    src = open(path, encoding="utf-8").read()
    out = replace_between(src, "<!-- SHOP:START -->", "<!-- SHOP:END -->", block)
    if "js/shop.js" not in out:
        out = out.replace('<script src="js/main.js"></script>', '<script src="js/main.js"></script>\n<script src="js/reviews-data.js"></script>\n<script src="js/shop.js"></script>')
    open(path, "w", encoding="utf-8").write(out)
    print("king.html:", len(cat), "products")


if __name__ == "__main__":
    main()
