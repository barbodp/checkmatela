"""Wire the approved heritage logo into the existing storefront and generators."""
from pathlib import Path
import re
import base64
ROOT = Path(__file__).resolve().parent.parent
data = base64.b64encode((ROOT/'brand/png/heritage-horizontal.png').read_bytes()).decode()
for name in ['heritage-horizontal', 'heritage-crest']:
    p = ROOT/f'brand/svg/{name}.svg'
    p.write_text(p.read_text().replace('../png/heritage-horizontal.png', 'data:image/png;base64,' + data))
for p in list(ROOT.glob('*.html')) + list((ROOT/'tools').rglob('*.py')):
    if p == Path(__file__).resolve():
        continue
    s = p.read_text()
    s = re.sub(r'brand/svg/compact-horizontal(?:-reverse)?\.svg\?v=2', 'brand/svg/heritage-horizontal.svg?v=1', s)
    s = s.replace('brand/svg/favicon.svg?v=2','brand/svg/heritage-crest.svg?v=1')
    s = s.replace('aria-label="Checkmatela home"','aria-label="Checkmate home"')
    s = re.sub(r'css/style\.css\?v=\d+', 'css/style.css?v=78', s)
    s = re.sub(r'CSS_VERSION = "\d+"', 'CSS_VERSION = "78"', s)
    p.write_text(s)
