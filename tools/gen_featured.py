"""Maintain the homepage's curated department tabs. Run from any directory."""
from pathlib import Path
import json
import re
from html import escape
ROOT = Path(__file__).resolve().parent.parent
catalog = json.loads((ROOT/'tools/catalog/king.json').read_text())['products']
def card(name, tag, price, image, href, alt):
    assert (ROOT/image).exists(), image
    assert (ROOT/href).exists(), href
    return f'<a class="featured-card" href="{href}"><div class="featured-card__image"><img loading="lazy" src="{image}" alt="{escape(alt)}"></div><h3>{escape(name)}</h3><p>{escape(tag)}</p><span>${price}</span></a>'
men = ''.join(card(p['name'], p['tag'], p['price'], 'assets/img/products/'+p['slug']+'.jpg', 'king.html', p['alt']) for p in [catalog[i] for i in [0,2,6,9]])
kids = ''.join(card(name,tag,price,f'assets/img/pawn/{line}/{color}/model-1.jpg',href,name+' on a child model') for name,tag,price,line,color,href in [
 ('Navy Slim Fit Suit','Modern fit · Kids',145,'slim-fit','navy','pawn-slim-fit.html'),
 ('Black Tuxedo','Black-tie occasions · Kids',159,'tuxedo','full-black','pawn-tuxedo.html'),
 ('Light Gray Vest Set','Celebrations & ring bearers · Kids',115,'suit-vest-set','light-gray','pawn-suit-vest-set.html'),
 ('Charcoal Husky Suit','Roomier fit · Kids',155,'husky-suit','charcoal','pawn-husky.html')])
section = '''<!-- ============ FEATURED OPENINGS — PRODUCT GRID ============ -->
<section class="section featured-departments" id="featured" aria-labelledby="featured-title">
<div class="container"><div class="section-head"><span class="eyebrow">Featured Openings</span>
<h2 id="featured-title">Find your next great look.</h2><p>Standout suits, tuxedos and occasionwear. Explore a few of our favorites for every generation.</p></div>
<div class="featured-tabs" role="tablist" aria-label="Featured collections">
'''
for department in ['men','women','kids']:
    section += f'<button type="button" role="tab" id="featured-tab-{department}" aria-controls="featured-{department}" aria-selected="{str(department=="men").lower()}" tabindex="{0 if department=="men" else -1}">{department.title()}</button>'
section += '</div><p class="featured-note">Collection preview. Prices are illustrative; online ordering is not connected.</p>'
for department,cards,href in [('men',men,'king.html'),('women','','queen.html'),('kids',kids,'pawn.html')]:
    section += f'<div role="tabpanel" id="featured-{department}" aria-labelledby="featured-tab-{department}" tabindex="0" {"hidden" if department!="men" else ""}>'
    if cards:
        section += f'<div class="featured-grid">{cards}</div><div class="grid-foot"><a class="btn dark-ghost" href="{href}">Explore {department.title()}</a></div>'
    else:
        section += '<div class="featured-coming"><svg class="glyph" aria-hidden="true"><use href="#glyph-queen"/></svg><span class="eyebrow">Coming Soon</span><h3>A new chapter in occasionwear.</h3><p>Our women’s collection is taking shape. There are no products available in this department yet.</p><a class="btn dark-ghost" href="queen.html">Explore Women</a></div>'
    section += '</div>'
section += '</div></section>\n\n'
p = ROOT/'index.html'
s = p.read_text()
s = re.sub(r'<!-- ============ FEATURED OPENINGS.*?(?=<!-- ============ BRAND STORY)',section,s,flags=re.S)
if 'js/featured.js' not in s:
    s = s.replace('</body>', '<script src="js/featured.js?v=1"></script>\n</body>')
p.write_text(s)
for p in list(ROOT.glob('*.html'))+list((ROOT/'tools').glob('gen_*.py')):
    s = re.sub(r'css/style\.css\?v=\d+', 'css/style.css?v=80', p.read_text())
    s = re.sub(r'CSS_VERSION = "\d+"', 'CSS_VERSION = "80"', s)
    p.write_text(s)
