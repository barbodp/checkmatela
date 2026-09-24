"""Transparent full-figure cutouts of the King (men's) product photos -> assets/img/king/<name>.webp
(used by the homepage showcase). Source: the white-background studio shots in assets/img/products/.

Run:  python3 tools/make_king_cutouts.py
"""
import os, glob
from PIL import Image
import cutlib
from make_hero_cutouts import save_webp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "assets", "img", "king")

def main():
    os.makedirs(DST, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(ROOT, "assets", "img", "products", "*.jpg"))):
        img = cutlib.keep_largest_alpha(cutlib.cutout(f))
        save_webp(img, os.path.join(DST, os.path.basename(f).replace(".jpg", ".webp")), height=1000)

if __name__ == "__main__":
    main()
