"""Optimises the raw Magen Kids product photography into assets/img/pawn/<line>/<colour>/{model,plain,thumb}-N.jpg

Order of shots in each product gallery: 4 model shots, then the plain (product-only) shots.
Raw file names are inconsistent (case, spaces, missing _1/_2), so everything is globbed per folder.

Needs:  pip install --user pillow
Run:  python3 tools/process_pawn_images.py
"""
import os, re, glob
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "assets", "img", "pawn")
SRC = os.path.expanduser("~/Downloads/Magen Kids")

# line slug -> raw top folder, raw model folder, [(raw plain-shot folder, raw model-shot folder, colour slug)]
LINES = {
    "suit-vest-set": ("Suit Vest Set", "Suit Vest Set w: Models",
                      [("Black", "Black", "black"), ("Indigo", "Indigo", "indigo"),
                       ("L-Gray", "Light Gray", "light-gray"), ("Navy", "Navy", "navy")]),
    "tuxedo-vest-set": ("Tuxedo Vest Set", "Tuxedo Vest Set w: Models",
                        [("Black", "Black", "black"), ("Burgundy", "Burgundy", "burgundy"),
                         ("L-Gray", "Light Gray", "light-gray"), ("L-Navy", "Light Navy", "light-navy")]),
    "slim-fit": ("Slim Fit", "Slim Fit w: Models",
                 [(f, f, s) for f, s in [
                     ("Black", "black"), ("Navy", "navy"), ("Charcoal", "charcoal"), ("L-Grey", "light-gray"),
                     ("M-Grey", "medium-gray"), ("White", "white"), ("Beige-Khaki", "beige-khaki"),
                     ("Khaki", "khaki"), ("Light Navy", "light-navy"), ("Royal-Blue", "royal-blue"),
                     ("Sky-Blue", "sky-blue"), ("Indigo-Blue", "indigo-blue"),
                     ("Hunter Green", "hunter-green"), ("Burgundy", "burgundy")]]),
    "tuxedo": ("Tuxedo TX-1026", "Tuxedo TX-1026 w: Models",
               [(f, f, s) for f, s in [
                   ("Full-Black", "full-black"), ("White-Black", "white-black"), ("Full-White", "full-white"),
                   ("Charcoal", "charcoal"), ("Shiny Charcoal", "shiny-charcoal"), ("Gray", "gray"),
                   ("Navy", "navy"), ("Royal-Blue", "royal-blue"), ("Red", "red"), ("Burgundy", "burgundy"),
                   ("Hunter Green", "hunter-green"), ("Khaki", "khaki")]]),
}


def to_rgb(im):
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "P", "LA"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[3])
        return bg
    return im.convert("RGB")


def save_main(src, dst, max_w=900, quality=82):
    im = to_rgb(Image.open(src))
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "JPEG", quality=quality, optimize=True)


def save_thumb(src, dst, y, size=160):
    im = ImageOps.fit(Image.open(src).convert("RGB"), (size, size), Image.LANCZOS, centering=(0.5, y))
    im.save(dst, "JPEG", quality=78, optimize=True)


def plain_key(path):
    m = re.search(r"_(\d)\.jpe?g$", path, re.I)
    return int(m.group(1)) if m else 9


def main():
    for line, (top, mdir, colours) in LINES.items():
        for plain_folder, model_folder, slug in colours:
            out = os.path.join(DST, line, slug)
            models = sorted(glob.glob(os.path.join(SRC, top, mdir, model_folder, "0*.png")))
            plains = sorted(glob.glob(os.path.join(SRC, top, plain_folder, "*.[jJ][pP]*[gG]")), key=plain_key)
            for i, p in enumerate(models, 1):
                save_main(p, os.path.join(out, f"model-{i}.jpg"))
            for i, p in enumerate(plains, 1):
                save_main(p, os.path.join(out, f"plain-{i}.jpg"))
            order = sorted(glob.glob(os.path.join(out, "model-*.jpg"))) + sorted(glob.glob(os.path.join(out, "plain-*.jpg")))
            for i, p in enumerate(order, 1):
                y = 0.0 if os.path.basename(p) in ("model-1.jpg", "model-2.jpg", "model-3.jpg") else 0.3
                save_thumb(p, os.path.join(out, f"thumb-{i}.jpg"), y)
            print(f"{line}/{slug}: {len(models)} model + {len(plains)} plain")


if __name__ == "__main__":
    main()
