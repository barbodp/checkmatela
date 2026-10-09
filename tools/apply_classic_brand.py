"""Apply the approved Classic Luxury identity without replacing storefront content."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
symbol = re.search(r'<symbol id="glyph-king"[^>]*>(.*?)</symbol>', (ROOT/'index.html').read_text(), re.S).group(1)
king = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 130" color="#a58a52">' + symbol + '</svg>'
(ROOT / 'brand/svg/classic-king.svg').write_text(king)
inner = king.split('>', 1)[1].rsplit('</svg>', 1)[0]
for suffix, color in [('', '#181818'), ('-reverse', '#F5F0E6')]:
    (ROOT / f'brand/svg/classic-horizontal{suffix}.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 120" role="img" aria-label="Checkmate">'
        '<title>Checkmate</title><g transform="translate(0 4) scale(.84)" color="#A58A52">' + inner + '</g>'
        f'<text x="103" y="77" fill="{color}" font-family="Georgia, Times New Roman, serif" font-size="53" letter-spacing="7">CHECKMATE</text></svg>')
files = list(ROOT.glob('*.html')) + list((ROOT/'tools').rglob('*.py')) + list((ROOT/'js').glob('*.js'))
for path in files:
    if path == Path(__file__).resolve():
        continue
    text = path.read_text()
    text = text.replace('Checkmatela', 'Checkmate')
    text = text.replace('brand/svg/compact-horizontal', 'brand/svg/classic-horizontal')
    text = text.replace('brand/svg/favicon.svg?v=2', 'brand/svg/classic-king.svg?v=1')
    text = re.sub(r'css/style\.css\?v=\d+', 'css/style.css?v=77', text)
    text = re.sub(r'CSS_VERSION = "\d+"', 'CSS_VERSION = "77"', text)
    path.write_text(text)
css = ROOT/'css/style.css'
text = css.read_text()
for old, new in {'#15181a':'#181818','#17191b':'#181818','#faf8f2':'#f5f0e6','#f0ebdd':'#eae3d7','#1e4d3b':'#181818','#0f2e22':'#181818','#4f8b71':'#68635b','#e7efe8':'#eee7db','#ad7f3c':'#a58a52','#d9b876':'#cfbc91','#8a6528':'#776238'}.items():
    text = text.replace(old, new)
addition = '''
/* Approved Classic Luxury: ivory, ink, restrained brass; retain the chessboard. */
.eyebrow:not(.on-dark){ color:var(--brass-deep); }
.eyebrow:not(.on-dark)::before{ background:var(--brass-deep); }
.btn{ border-radius:0; }
.site-header::before{ background:rgba(245,240,230,.97); }
.product-card__price,.gallery-card__price{ color:var(--ink); }
'''
if 'Approved Classic Luxury:' not in text:
    text += addition
css.write_text(text)
