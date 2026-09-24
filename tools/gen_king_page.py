"""Generate the King grid from tools/catalog/king.json, then run gen_catalog.py."""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    products = json.loads((ROOT / 'tools/catalog/king.json').read_text())['products']
    cards = []
    for p in products:
        ident = 'king-' + p['slug']
        cards.append(f'''      <a class="product-card" href="#{ident}" id="{ident}" data-product="{ident}">
        <div class="product-card__frame"><img src="assets/img/products/{p['slug']}.jpg" alt="{escape(p['alt'])}" loading="lazy"><span class="product-card__notation">{escape(p['notation'])}</span><span class="product-card__quick"><span class="btn small">Explore the piece ↗</span></span></div>
        <div class="product-card__meta"><div><h4>{escape(p['name'])}</h4><span class="piece-tag">{escape(p['tag'])}</span></div><span class="product-card__price">${p['price']}</span></div>
      </a>''')
    page = ROOT / 'king.html'
    source = page.read_text()
    source = re.sub(r'(<div class="product-grid"[^>]*>).*?(\n    </div>\n  </div>\n</section>)',lambda m:m.group(1)+'\n'+'\n'.join(cards)+m.group(2),source,count=1,flags=re.S)
    source = re.sub(r'(<span class="filter-bar__count">).*?(</span>)',lambda m:m.group(1)+f'{len(products)} openings in this collection'+m.group(2),source,count=1)
    page.write_text(source)
    print('wrote king.html',len(products),'products')

if __name__ == '__main__':
    main()
