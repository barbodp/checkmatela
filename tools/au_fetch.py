"""Antonio Uomo (our dropship supplier) -> catalog + image library.

1. Reads https://www.antoniouomo.com/products.json (every product is a men's piece) and normalises it into tools/catalog/antonio-uomo.json
   (type, "<Colour> <Style name>", style code, price, copy, bullets, sizes/lengths, image list).
2. Downloads every original image into  ~/Downloads/Antonio Uomo/<Product type>/<Colour Style name (code)>/NN.jpg  (resumable: existing files are kept).
3. Writes web-sized copies into assets/img/antonio-uomo/ (content-addressed by md5, so images shared between products are stored once):
   <md5>.webp (max 900px wide), <md5>-t.webp (160px thumb), and <md5>-c.webp (480px card image).

4. Reads the size chart each product page pops up ("Size Chart" button) and stores its id on the product (`chart`); the chart data itself is transcribed in tools/au_sizes.py.

Run from anywhere:  python3 tools/au_fetch.py [--no-download] [--no-optimize] [--charts-only]
"""
import os, re, sys, json, html, hashlib, urllib.request, concurrent.futures as cf
from html.parser import HTMLParser
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "tools", "catalog", "antonio-uomo.json")
DL = os.path.expanduser("~/Downloads/Antonio Uomo")
ASSETS = os.path.join(ROOT, "assets", "img", "antonio-uomo")
UA = {"User-Agent": "Mozilla/5.0"}

# titles that carry no colour (the supplier left it out) — checked against the photos / URL handle
COLOUR_FIX = {"560811": "Dark Teal", "107111": "Shiny Black"}
# supplier type name -> (plural for the type page, singular style name used in "<Colour> <Style name>")
PLURAL = {"Suit": "Suits", "Tuxedo": "Tuxedos", "Jacket": "Jackets", "Pants": "Pants"}

FAMILY_RULES = [("navy", "Navy"), ("midnight", "Navy"), ("indigo", "Blue"), ("royal", "Blue"), ("french", "Blue"), ("powder", "Blue"), ("sky", "Blue"),
                ("blue", "Blue"), ("teal", "Teal"), ("charcoal", "Charcoal"), ("silver", "Silver"), ("grey", "Grey"), ("gray", "Grey"), ("black", "Black"),
                ("burgundy", "Burgundy"), ("maroon", "Burgundy"), ("wine", "Burgundy"), ("red", "Red"), ("green", "Green"), ("brown", "Brown"),
                ("beige", "Beige"), ("tan", "Beige"), ("khaki", "Beige"), ("cream", "Beige"), ("gold", "Gold"), ("white", "White"), ("pink", "Pink"), ("purple", "Purple")]


def family(colour):
    c = colour.lower()
    for key, fam in FAMILY_RULES:
        if key in c:
            return fam
    return "Other"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def fs_name(s):
    return re.sub(r'[\\/:*?"<>|]+', "-", s).strip()


class Body(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paras, self.bullets, self._buf, self._in = [], [], "", None

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "li", "div") and self._in is None:
            self._in, self._buf = tag, ""
        if tag == "br":
            self._buf += " "

    def handle_endtag(self, tag):
        if tag == self._in:
            t = re.sub(r"\s+", " ", self._buf).strip()
            if t:
                (self.bullets if tag == "li" else self.paras).append(t)
            self._in = None

    def handle_data(self, d):
        if self._in:
            self._buf += d


def parse_body(raw):
    b = Body()
    b.feed(raw or "")
    b.close()
    seen, paras = set(), []
    for p in b.paras:
        if p not in seen:
            seen.add(p); paras.append(p)
    return paras, b.bullets


def normalise(prods):
    items = []
    for p in prods:
        title = html.unescape(p["title"]).strip()
        m = re.search(r"\(([^)]+)\)\s*$", title)
        code = m.group(1) if m else ""
        base = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
        if " - " in base:
            style, colour = [x.strip() for x in base.split(" - ", 1)]
        elif re.search(r"Patterned Jacket$", base):
            style = "Patterned Jacket"; colour = base[: -len(style)].strip()
        else:
            style, colour = base, ""
        colour = COLOUR_FIX.get(code, colour)
        if not colour:
            raise SystemExit(f"no colour for {title}")
        style = re.sub(r"Suits$", "Suit", style)                     # singular for the product name
        style = style.replace("Tuxedos", "Tuxedo")
        last = style.split()[-1]
        type_plural = style if last in ("Pants", "Jackets") else style + "s"
        type_plural = type_plural.replace("Jacket" + "s", "Jackets")
        if style.endswith("Jacket"):
            type_plural = style + "s"
        paras, bullets = parse_body(p["body_html"])
        prices = [float(v["price"]) for v in p["variants"]]
        sizes = next((o["values"] for o in p["options"] if o["name"].lower() == "size"), [])
        lengths = next((o["values"] for o in p["options"] if o["name"].lower() == "length"), [])
        order = {"Short": 0, "Regular": 1, "Long": 2}
        lengths = sorted(lengths, key=lambda v: order.get(v, 9))
        items.append(dict(
            handle=p["handle"], code=code, colour=colour, family=family(colour), style=style, type=type_plural, type_slug=slug(type_plural),
            name=f"{colour} {style}", slug=slug(f"{style} {colour} {code}"), price=int(min(prices)) if min(prices) == int(min(prices)) else min(prices),
            paras=paras, bullets=bullets, sizes=sizes, lengths=lengths, tags=p.get("tags", []),
            images=[dict(src=i["src"], w=i["width"], h=i["height"]) for i in p["images"]],
            supplier_url="https://www.antoniouomo.com/products/" + p["handle"],
        ))
    return items


def fetch_products():
    out, page = [], 1
    while True:
        req = urllib.request.Request(f"https://www.antoniouomo.com/products.json?limit=250&page={page}", headers=UA)
        data = json.load(urllib.request.urlopen(req, timeout=60))["products"]
        if not data:
            return out
        out += data
        page += 1


def chart_of(handle):
    """id of the size-chart image shown in the product page's pop-up (e.g. 'SIZE-CHART-MAY-3'), '' when there is none."""
    t = urllib.request.urlopen(urllib.request.Request("https://www.antoniouomo.com/products/" + handle, headers=UA), timeout=60).read().decode("utf-8", "ignore")
    m = re.search(r"<modal-dialog.*?</modal-dialog>", t, re.S)
    im = re.search(r"files/([A-Za-z0-9_-]+?)(?:_\d+x\d*)?\.(?:jpg|jpeg|png|webp)", m.group(0)) if m else None
    return im.group(1) if im else ""


def ext_of(url):
    e = os.path.splitext(url.split("?")[0])[1].lower()
    return e if e in (".jpg", ".jpeg", ".png", ".webp") else ".jpg"


def download_one(args):
    url, dest = args
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest, "kept"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for attempt in range(4):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
            with open(dest, "wb") as f:
                f.write(data)
            return dest, "ok"
        except Exception as e:                                          # noqa: BLE001
            last = e
    return dest, f"FAILED {last}"


def to_rgb(im):
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA"); bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); return bg
    return im.convert("RGB")


def optimise(path):
    """-> md5 key of the original; writes <key>.webp / -t.webp / -c.webp (skipped when they exist)."""
    key = hashlib.md5(open(path, "rb").read()).hexdigest()[:12]
    main, thumb, card = (os.path.join(ASSETS, key + s) for s in (".webp", "-t.webp", "-c.webp"))
    if not (os.path.exists(main) and os.path.exists(thumb) and os.path.exists(card)):
        im = to_rgb(Image.open(path))
        def sized(w):
            return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) if im.width > w else im
        sized(900).save(main, "WEBP", quality=76, method=5)
        sized(480).save(card, "WEBP", quality=74, method=5)
        ImageOps.fit(im, (160, 160), Image.LANCZOS, centering=(0.5, 0.12 if im.height > im.width else 0.5)).save(thumb, "WEBP", quality=70, method=5)
    return key


def charts_only():
    items = json.load(open(OUT_JSON, encoding="utf-8"))
    with cf.ThreadPoolExecutor(8) as ex:
        for it, c in zip(items, ex.map(lambda i: chart_of(i["handle"]), items)):
            it["chart"] = c
    json.dump(items, open(OUT_JSON, "w"), indent=1, ensure_ascii=False)
    print("charts:", {c: sum(1 for i in items if i["chart"] == c) for c in sorted({i["chart"] for i in items})})


def main():
    if "--charts-only" in sys.argv:
        return charts_only()
    prods = fetch_products()
    items = normalise(prods)
    for it in items:
        it["folder"] = os.path.join(DL, fs_name(it["type"]), fs_name(f"{it['name']} ({it['code']})"))
        for n, img in enumerate(it["images"], 1):
            img["file"] = os.path.join(it["folder"], f"{n:02d}{ext_of(img['src'])}")
    if "--no-download" not in sys.argv:
        jobs = [(img["src"], img["file"]) for it in items for img in it["images"]]
        done = 0
        with cf.ThreadPoolExecutor(8) as ex:
            for dest, status in ex.map(download_one, jobs):
                done += 1
                if status.startswith("FAILED"):
                    print(status, dest)
                if done % 50 == 0:
                    print(f"downloaded {done}/{len(jobs)}", flush=True)
        print("download finished:", len(jobs), "images")
    if "--no-optimize" not in sys.argv:
        os.makedirs(ASSETS, exist_ok=True)
        files = [img["file"] for it in items for img in it["images"]]
        with cf.ThreadPoolExecutor(4) as ex:
            keys = list(ex.map(optimise, files))
        it_keys = iter(keys)
        for it in items:
            for img in it["images"]:
                img["key"] = next(it_keys)
        print("optimised", len(files), "images ->", len(set(keys)), "unique files")
    with cf.ThreadPoolExecutor(8) as ex:
        for it, c in zip(items, ex.map(lambda i: chart_of(i["handle"]), items)):
            it["chart"] = c
    for it in items:
        it.pop("folder", None)
        for img in it["images"]:
            img.pop("file", None)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(items, open(OUT_JSON, "w"), indent=1, ensure_ascii=False)
    print("wrote", os.path.relpath(OUT_JSON, ROOT), len(items), "products")


if __name__ == "__main__":
    main()
