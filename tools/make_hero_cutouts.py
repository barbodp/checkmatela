"""Builds the transparent full-figure cutouts used by the category heroes (assets/img/**/hero.webp, assets/img/hero/cat-*.webp).

Needs:  pip install --user pillow numpy scipy
Kid models are cut out of the raw 01-front.png shots in ~/Downloads/Magen Kids (white studio background).
Run:  python3 tools/make_hero_cutouts.py
"""
import os
import numpy as np
from PIL import Image
import cutlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
SRC = os.path.expanduser("~/Downloads/Magen Kids")

# (line slug, colour slug, raw top folder, raw model folder, raw colour folder)
KIDS = [
    ("slim-fit", "navy", "Slim Fit", "Slim Fit w: Models", "Navy"),
    ("slim-fit", "burgundy", "Slim Fit", "Slim Fit w: Models", "Burgundy"),
    ("slim-fit", "hunter-green", "Slim Fit", "Slim Fit w: Models", "Hunter Green"),
    ("suit-vest-set", "black", "Suit Vest Set", "Suit Vest Set w: Models", "Black"),
    ("suit-vest-set", "indigo", "Suit Vest Set", "Suit Vest Set w: Models", "Indigo"),
    ("suit-vest-set", "navy", "Suit Vest Set", "Suit Vest Set w: Models", "Navy"),
    ("tuxedo", "full-black", "Tuxedo TX-1026", "Tuxedo TX-1026 w: Models", "Full-Black"),
    ("tuxedo", "red", "Tuxedo TX-1026", "Tuxedo TX-1026 w: Models", "Red"),
    ("tuxedo", "royal-blue", "Tuxedo TX-1026", "Tuxedo TX-1026 w: Models", "Royal-Blue"),
    ("tuxedo-vest-set", "black", "Tuxedo Vest Set", "Tuxedo Vest Set w: Models", "Black"),
    ("tuxedo-vest-set", "burgundy", "Tuxedo Vest Set", "Tuxedo Vest Set w: Models", "Burgundy"),
    ("tuxedo-vest-set", "light-navy", "Tuxedo Vest Set", "Tuxedo Vest Set w: Models", "Light Navy"),
]
# NOTE: the foot-shadow rule in cutlib removes light-grey pixels in the bottom 20% of the frame,
# so avoid light-grey / white trousers for hero figures (use the darker colourways).


def bbox_crop(im):
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())


def save_webp(img, dst, height=None, width=None, quality=86):
    if height:
        img = img.resize((round(img.width * height / img.height), height), Image.LANCZOS)
    if width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    img.save(dst, "WEBP", quality=quality, method=5)
    print(os.path.relpath(dst, ROOT), img.size, os.path.getsize(dst) // 1024, "KB")


def main():
    for line, slug, top, mdir, folder in KIDS:
        raw = os.path.join(SRC, top, mdir, folder, "01-front.png")
        save_webp(cutlib.cutout(raw), os.path.join(IMG, "pawn", line, slug, "hero.webp"), height=1000)

    # Men's models for the King hero: the existing transparent homepage cutouts, cropped tight
    for src, name in [("hero-suit-blue.png", "cat-king-blue.webp"), ("hero-suit.png", "cat-king-black.webp"),
                      ("hero-suit-burg.png", "cat-king-burgundy.webp")]:
        im = bbox_crop(cutlib.keep_largest_alpha(Image.open(os.path.join(IMG, "hero", src)).convert("RGBA")))
        save_webp(im, os.path.join(IMG, "hero", name), height=1000, quality=88)

    # Shoes: wide crop of the raw studio shot so the whole pair (incl. toe) is kept, shadow removed
    raw = Image.open(os.path.join(IMG, "diagram_raw", "shoes.png")).convert("RGB")
    W, H = raw.size
    crop = raw.crop((int(W * 0.10), int(H * 0.30), int(W * 0.93), int(H * 0.86)))
    arr = np.asarray(crop).astype(np.int16)
    out = bbox_crop(cutlib.defringe_and_feather(arr, cutlib.make_alpha(arr, near=226, sat=22, shadow_band=0.86)))
    save_webp(out, os.path.join(IMG, "hero", "cat-shoes.webp"), width=900, quality=88)

    # Bow tie + cufflinks: looser threshold drops the floor shadow (dark/gold objects)
    for name in ["bowtie", "cufflinks"]:
        raw = Image.open(os.path.join(IMG, "diagram_raw", f"{name}.png")).convert("RGB")
        arr = np.asarray(raw).astype(np.int16)
        out = bbox_crop(cutlib.defringe_and_feather(arr, cutlib.make_alpha(arr, near=226, sat=26, shadow_band=1.1)))
        save_webp(out, os.path.join(IMG, "hero", f"cat-{name}.webp"), width=900, quality=88)

    # Pocket square: white object, its shadow can't be separated — reuse the diagram cutout
    ps = Image.open(os.path.join(IMG, "diagram", "pocketsquare.png")).convert("RGBA")
    save_webp(ps, os.path.join(IMG, "hero", "cat-pocketsquare.webp"), width=700, quality=88)


if __name__ == "__main__":
    main()
