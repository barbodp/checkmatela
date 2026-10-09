"""Publish the corrected logo and an ivory-lettered transparent footer variant."""
from pathlib import Path
import base64
import re
ROOT = Path(__file__).resolve().parent.parent
data = base64.b64encode((ROOT/'brand/png/heritage-horizontal-v2.png').read_bytes()).decode()
image = f'<image href="data:image/png;base64,{data}" width="2172" height="724"/>'
start = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="110 110 1960 500" role="img" aria-label="Checkmate"><title>Checkmate</title>'
(ROOT/'brand/svg/heritage-horizontal.svg').write_text(start + image + '</svg>')
defs = '<defs><clipPath id="crest"><rect width="510" height="724"/></clipPath><clipPath id="letters"><rect x="510" width="1662" height="724"/></clipPath><filter id="ivory" color-interpolation-filters="sRGB"><feFlood flood-color="#faf8f2"/><feComposite in2="SourceAlpha" operator="in"/></filter></defs>'
(ROOT/'brand/svg/heritage-footer.svg').write_text(start + defs + '<g clip-path="url(#crest)">' + image + '</g><g clip-path="url(#letters)" filter="url(#ivory)">' + image + '</g></svg>')
for p in list(ROOT.glob('*.html')) + list((ROOT/'tools').rglob('*.py')):
    if p.name in ['refine_heritage_logo.py', 'apply_heritage_logo.py']:
        continue
    s = p.read_text().replace('heritage-horizontal.svg?v=1','heritage-horizontal.svg?v=2')
    s = re.sub(r'(<div class="footer-brand">\s*<a[^>]*><img src=")brand/svg/heritage-horizontal.svg\?v=2', r'\1brand/svg/heritage-footer.svg?v=2', s)
    s = re.sub(r'css/style\.css\?v=\d+', 'css/style.css?v=79', s)
    s = re.sub(r'CSS_VERSION = "\d+"', 'CSS_VERSION = "79"', s)
    p.write_text(s)
