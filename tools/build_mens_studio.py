"""Rebuild one men's studio collection and its product pages."""
import gen_gioberti as catalog
import re
import sys
from pathlib import Path

if __name__ == '__main__':
    category = sys.argv[1]
    if category not in ('men-polo-shirts', 'men-sweaters', 'men-jackets', 'men-leather-jackets'):
        raise ValueError(category)
    catalog.build_category(category)
    items = [item for item in catalog.ITEMS if item['cat'] == category]
    for item in items:
        catalog.build_product(item)
    covers = {item['file']: catalog.casual_studio.cover(item, catalog.cover(item)) for item in items}
    updated = []
    for page in Path(catalog.ROOT).glob('*.html'):
        original = page.read_text(encoding='utf-8')
        def update_card(match):
            card = match.group()
            href = re.search(r'\bhref="([^"]+)"', card)
            model = covers.get(href.group(1)) if href else None
            if not model:
                return card
            card = re.sub(r'\bdata-img="[^"]+"', f'data-img="{model}"', card, count=1)
            return re.sub(r'(<img\b[^>]*\bsrc=")[^"]+', lambda m: m.group(1) + model, card, count=1)
        text = re.sub(r'<a\b[^>]*class="product-card[^>]*>.*?</a>', update_card, original, flags=re.S)
        if text != original:
            page.write_text(text, encoding='utf-8', newline='\n')
            updated.append(page.name)
    print(f'Rebuilt {len(items)} product pages.')
    print('Updated model covers on: ' + ', '.join(updated) if updated else 'Collection covers are current.')
