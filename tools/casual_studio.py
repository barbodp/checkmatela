"""Color-isolated studio galleries, kept separate from supplier stock data."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFESTS = ['casual-shirt-studio.json', 'flannel-studio.json']
STUDIO = []
for name in MANIFESTS:
    manifest = ROOT / 'tools/catalog' / name
    if manifest.exists():
        STUDIO.extend(json.loads(manifest.read_text(encoding='utf-8'))['images'])
ANGLES = {'front': 'Front view', 'threequarter': 'Three-quarter view', 'back': 'Back view'}
esc = lambda value: html.escape(str(value), quote=True)


def cover(item, default):
    colors = item.get('all_colours') or item['colours']
    color = next((c for c in colors if item['colour_img'].get(c) == default), colors[0] if colors else None)
    return next((im['src'] for im in STUDIO if im['handle'] == item['handle'] and im['color'] == color and im['angle'] == 'front'), None)


def gallery(item, photos, cover):
    colors = item['options'][0]['values']
    chosen = next((c for c in colors if item['colour_img'].get(c) == cover), colors[0])
    images = []
    for color in colors:
        modeled = [im for im in STUDIO if im['handle'] == item['handle'] and im['color'] == color]
        modeled.sort(key=lambda im: list(ANGLES).index(im['angle']))
        for im in modeled:
            if not (ROOT / im['src']).is_file():
                raise FileNotFoundError(im['src'])
            images.append(dict(src=im['src'], thumb=im['src'].replace('.webp','-t.webp'), w=im['w'], h=im['h'], color=color, label=ANGLES[im['angle']]))
        for im in photos:
            # Untagged supplier photos cannot reliably belong to a color set.
            if color not in (im.get('colours') or []):
                continue
            images.append(dict(src=f"assets/img/gioberti/{im['key']}.webp", thumb=f"assets/img/gioberti/{im['key']}-t.webp", w=im['w'], h=im['h'], color=color, label='Product photo'))
    first = next(im for im in images if im['color'] == chosen)
    thumbs = []
    for im in images:
        active = im is first
        label = f"{item['name']} — {im['color']} — {im['label']}"
        thumbs.append(f'<button type="button" class="pdp-thumb{" is-active" if active else ""}" data-src="{esc(im["src"])}" data-w="{im["w"]}" data-h="{im["h"]}" data-colour="{esc(im["color"])}" data-label="{esc(label)}" aria-label="{esc(label)}" aria-pressed="{str(active).lower()}"{" hidden" if im["color"] != chosen else ""}><img src="{esc(im["thumb"])}" alt="" loading="lazy" width="72" height="72"></button>')
    return (f'<div class="pdp-gallery" data-color-gallery><div class="pdp-main" id="pdpFrame" style="--r:0.6667">'
            f'<img id="pdpMain" src="{esc(first["src"])}" alt="{esc(item["name"])} — {esc(chosen)} — {first["label"]}" width="{first["w"]}" height="{first["h"]}" fetchpriority="high"></div>'
            '<div class="pdp-gallery-nav"><button type="button" data-gallery-prev aria-label="Previous photo">←</button><span data-gallery-status aria-live="polite" aria-atomic="true"></span><button type="button" data-gallery-next aria-label="Next photo">→</button></div>'
            f'<div class="pdp-thumbs" aria-label="Photos for the selected color">{"".join(thumbs)}</div></div>')
