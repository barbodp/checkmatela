"""Shared HTML for the filterable, comparable product grids (King page, Pawn style pages, and any category added later).

The behaviour lives in js/shop.js and is driven entirely by data attributes on the cards:
    data-id, data-name, data-tag, data-price, data-img, data-f-<facet>="Value|Other value"
and by data-facets on the wrapper (which facets exist and their labels). Facets with fewer than two distinct values
are hidden automatically, so adding a new attribute to the cards is all it takes to get a new filter group.
"""
import json, html
import numpy as np
from PIL import Image

esc = html.escape

SORTS = [("featured", "Featured"), ("price-asc", "Price: Low to High"), ("price-desc", "Price: High to Low"), ("name", "Name: A to Z")]


def shop_block(cards_html, facets, kind, grid_class="product-grid", count_noun="products", review_facets=None, extra_attrs=""):
    """facets: [{"key": "color", "label": "Colour", "swatch": True}, ...]"""
    rf = review_facets or []
    sorts = "".join(f'<option value="{v}">{l}</option>' for v, l in SORTS)
    return f'''<section class="section shop-section" style="padding-top:28px">
  <div class="container">
    <div class="shop" data-shop data-kind="{kind}" data-noun="{esc(count_noun)}" data-facets='{json.dumps(facets)}' data-review-facets='{json.dumps(rf)}'{extra_attrs}>
      <div class="shop-bar">
        <button type="button" class="shop-filter-btn" aria-expanded="false">Filters <span class="shop-filter-btn__n"></span></button>
        <span class="shop-count" aria-live="polite"></span>
        <label class="filter-bar__sort">Sort by
          <select class="shop-sort">{sorts}</select>
        </label>
      </div>
      <div class="shop-chips" aria-label="Active filters"></div>
      <div class="shop-layout">
        <aside class="shop-filters" aria-label="Filters"></aside>
        <div class="shop-results">
          <div class="{grid_class}" data-grid>
{cards_html}
          </div>
          <p class="shop-empty" hidden>No pieces match those filters. <button type="button" class="shop-clear">Clear all filters</button></p>
        </div>
      </div>
    </div>
  </div>
</section>'''


def replace_between(src, start, end, block):
    i, j = src.index(start) + len(start), src.index(end)
    return src[:i] + "\n" + block + "\n" + src[j:]


def swatch_hex(path):
    """Dominant garment colour of a cutout (ignores near-white shirt/skin) — used for colour dots and light/dark tone."""
    im = np.asarray(Image.open(path).convert("RGBA"))
    h, w, _ = im.shape
    reg = im[int(h * .28):int(h * .68), int(w * .28):int(w * .72)].reshape(-1, 4)
    reg = reg[reg[:, 3] > 200][:, :3].astype(int)
    reg = reg[reg.min(axis=1) < 205]
    if len(reg) == 0:
        return "#cccccc"
    q = reg // 32
    keys = q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2]
    mode = np.bincount(keys).argmax()
    m = reg[keys == mode].mean(axis=0).astype(int)
    return "#%02x%02x%02x" % tuple(m)


def tone_of(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    lum = .299 * r + .587 * g + .114 * b
    return "Dark" if lum < 75 else ("Mid" if lum < 150 else "Light")
