"""Gioberti (our dropship supplier for men's and boys' formal and casual wear) -> catalog + image library. Same pipeline as tools/au_fetch.py.

1. Reads https://gioberti.com/products.json and normalises it into tools/catalog/gioberti.json: title, product type, style code, options
   (colour first, then size), every variant with its price and availability, copy, and the photo for each colour.
2. Downloads every original image into the photo archive  ~/Downloads/Gioberti/<Men|Boys - Category>/<Style number - Colour>/NN.jpg
   (shared photos and the size chart in <Style number - All Colours>; see archive_paths(). Resumable: existing files are kept).
3. Writes web-sized copies into assets/img/gioberti/ (content-addressed by md5, like Antonio Uomo):
   <md5>.webp (max 900px wide), <md5>-t.webp (160px thumb), <md5>-c.webp (480px card image).
   Size charts: Gioberti adds the product's own size chart as one of its photos (alt / file name "size chart"); it is kept out of the
   gallery and saved larger (<md5>-z.webp, max 1400px) so the numbers stay readable in the product's "Size chart" pop-up.

Run from anywhere:  python3 tools/gb_fetch.py [--update] [--no-download] [--no-optimize]
(--update = quick stock/price refresh that only downloads new photos; the scheduled GitHub Action uses it)
The gift card is left out; sold-out products are kept (`soldout`) and shown as sold out; tools/gen_gioberti.py builds the pages from the JSON.
"""
import os, re, sys, json, html, hashlib, urllib.request, concurrent.futures as cf
from PIL import Image, ImageOps
from au_fetch import parse_body, download_one, ext_of, to_rgb, fs_name, slug
from gb_catalog import category_of, folder_label

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "tools", "catalog", "gioberti.json")
DL = os.path.expanduser("~/Downloads/Gioberti")
ASSETS = os.path.join(ROOT, "assets", "img", "gioberti")
UA = {"User-Agent": "Mozilla/5.0"}
SHOP = "https://gioberti.com"

# Colour families (same names as the rest of the site's filters). A colour can belong to two families ("Metallic Black / Gold").
FAMILY_RULES = [
    ("Charcoal", r"charcoal|\bd gray\b|dark gr[ae]y|smoky"), ("Grey", r"(?<!d )(?<!dark )\b(gr[ae]y|heather|h gray|marled)\b"), ("Black", r"black"),
    ("Navy", r"navy|midnight|indigo|dark blue"), ("Blue", r"(?<!dark )(?<!midnight )blue|royal|aqua|turquoise|denim|\bsky\b"), ("Teal", r"teal"),
    ("White", r"white|ivory|cream|\boff\b"), ("Beige", r"beige|khaki|\btan\b|stone|camel|sand|oat"), ("Brown", r"brown|coffee|umber|mocha|chocolate|rust"),
    ("Green", r"green|olive|mint|sage|hunter|forest"), ("Burgundy", r"burgundy|burgurdy|wine|maroon|crimson"), ("Red", r"\bred\b"),
    ("Pink", r"pink|coral|fuchsia|rose|blush"), ("Purple", r"purple|lilac|lavender|violet|plum"), ("Yellow", r"yellow|banana|mustard"),
    ("Gold", r"gold"), ("Orange", r"orange"), ("Silver", r"silver"),
]


def families(colours):
    out = []
    for c in colours:
        for fam, rx in FAMILY_RULES:
            if re.search(rx, c, re.I) and fam not in out:
                out.append(fam)
    return out or ["Other"]


def is_chart(im):
    return bool(re.search(r"size|chart", (im.get("alt") or "") + " " + im["src"].split("?")[0].rsplit("/", 1)[-1], re.I))


def fetch_products():
    out, page = [], 1
    while True:
        req = urllib.request.Request(f"{SHOP}/products.json?limit=250&page={page}", headers=UA)
        data = json.load(urllib.request.urlopen(req, timeout=60))["products"]
        if not data:
            return out
        out += data
        page += 1


def normalise(prods):
    items, skipped = [], []
    for p in prods:
        if p["product_type"] == "Gift Card":
            continue
        soldout = not any(v["available"] for v in p["variants"])           # kept and shown as "Sold out"
        if soldout:
            skipped.append(p["handle"])
        opts = [o for o in p["options"] if not (o["name"] == "Title" and o["values"] == ["Default Title"])]
        ci = next((i for i, o in enumerate(opts) if re.match(r"colou?r", o["name"], re.I)), None)
        order = ([ci] if ci is not None else []) + [i for i in range(len(opts)) if i != ci]      # colour first, then size
        pos = [o["position"] - 1 for o in opts]
        variants = []
        for v in p["variants"]:
            vals = [v["option1"], v["option2"], v["option3"]]
            variants.append(dict(o=[vals[pos[i]] for i in order], price=float(v["price"]), ok=bool(v["available"]),
                                 img=(v.get("featured_image") or {}).get("id")))
        options = [dict(name=opts[i]["name"], values=opts[i]["values"]) for i in order]
        live = [v for v in variants if v["ok"]] or variants                # a sold-out product: price / colours from every variant
        colours = [c for c in options[0]["values"] if any(v["o"][0] == c for v in live)] if ci is not None else []
        all_colours = list(options[0]["values"]) if ci is not None else []
        colour_img = {}
        for v in variants:
            if ci is not None and v["img"] and v["o"][0] not in colour_img:
                colour_img[v["o"][0]] = v["img"]
        paras, bullets = parse_body(p["body_html"])
        vcol = {v["id"]: [v["option1"], v["option2"], v["option3"]][pos[ci]] for v in p["variants"]} if ci is not None else {}
        images = [dict(id=i["id"], src=i["src"], w=i["width"], h=i["height"], chart=is_chart(i),
                       colours=[c for c in options[0]["values"] if c in {vcol.get(v) for v in i.get("variant_ids", [])}] if ci is not None else []) for i in p["images"]]
        prices = [v["price"] for v in live]
        items.append(dict(
            handle=p["handle"], name=html.unescape(p["title"]).strip(), ptype=p["product_type"], code=(p["variants"][0].get("sku") or "").split(":")[0],
            options=options, variants=[[*v["o"], v["price"], int(v["ok"])] for v in variants], soldout=soldout,
            colours=colours, all_colours=all_colours, families=families(all_colours),
            colour_img={c: i for c, i in colour_img.items()}, price=min(prices), price_max=max(prices),
            paras=paras, bullets=bullets, images=images, supplier_url=f"{SHOP}/products/{p['handle']}",
        ))
    return items, skipped


def optimise(path, chart=False):
    """-> md5 key of the original; writes <key>.webp / -t.webp / -c.webp (and -z.webp for size charts), skipped when they exist."""
    key = hashlib.md5(open(path, "rb").read()).hexdigest()[:12]
    outs = {s: os.path.join(ASSETS, key + s) for s in ((".webp", "-t.webp", "-c.webp") + (("-z.webp",) if chart else ()))}
    if not all(os.path.exists(f) for f in outs.values()):
        im = to_rgb(Image.open(path))
        def sized(w):
            return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) if im.width > w else im
        sized(900).save(outs[".webp"], "WEBP", quality=76, method=5)
        sized(480).save(outs["-c.webp"], "WEBP", quality=74, method=5)
        ImageOps.fit(im, (160, 160), Image.LANCZOS, centering=(0.5, 0.12 if im.height > im.width else 0.5)).save(outs["-t.webp"], "WEBP", quality=70, method=5)
        if chart:
            sized(1400).save(outs["-z.webp"], "WEBP", quality=88, method=5)
    return key


def archive_paths(items):
    """~/Downloads/Gioberti/<Men|Boys - Category>/<Style - Colour>/NN.jpg: each photo in the folder of the colour it shows (a photo of two colours
    goes in both); photos of no single colour (details, lifestyle) and the size chart go in <Style - All Colours>. When two products share a style
    number, the product name is added to the folder ("VSM-96P (Men's 4 pc Paisley Vest Set) - Red")."""
    shared = {c for c in (i["code"] for i in items) if sum(1 for j in items if j["code"] == c) > 1}
    same_name = {(i["code"], i["name"]) for i in items if sum(1 for j in items if (j["code"], j["name"]) == (i["code"], i["name"])) > 1}
    for it in items:
        cat = category_of(it["handle"], it["ptype"], it["name"])
        base = os.path.join(DL, fs_name(folder_label(it["handle"], cat) if cat else it["ptype"]))
        style = it["code"] or it["handle"]
        if style in shared:                                    # same style number, same name too -> the supplier's URL handle tells them apart
            style = f"{style} ({it['handle'] if (it['code'], it['name']) in same_name else it['name']})"
        count = {}
        for im in it["images"]:
            folders = [f"{style} - {c}" for c in im["colours"]] or [f"{style} - All Colours" if it["colours"] else style]
            im["files"] = []
            for fo in folders:
                if im["chart"] and not im["colours"]:
                    count["chart " + fo] = count.get("chart " + fo, 0) + 1
                    name = "Size Chart" + ("" if count["chart " + fo] == 1 else f" {count['chart ' + fo]}")
                else:
                    count[fo] = count.get(fo, 0) + 1
                    name = f"{count[fo]:02d}"
                im["files"].append(os.path.join(base, fs_name(fo), name + ext_of(im["src"])))


def main():
    """Full run: download every photo (archive) and (re)build the web copies. --update: the quick run used by the scheduled stock sync
    (.github/workflows/gioberti-stock.yml): stock, prices and products are refreshed, and only photos not seen before are downloaded."""
    update = "--update" in sys.argv
    items, skipped = normalise(fetch_products())
    archive_paths(items)
    known = {}                                                            # photo URL -> web copy key, from the previous catalog
    if update and os.path.exists(OUT_JSON):
        for it in json.load(open(OUT_JSON, encoding="utf-8")):
            for im in it["images"]:
                k = im.get("key")
                if im.get("url") and k and os.path.exists(os.path.join(ASSETS, k + ".webp")) and (not im["chart"] or os.path.exists(os.path.join(ASSETS, k + "-z.webp"))):
                    known[im["url"]] = k
    ims = [im for it in items for im in it["images"]]
    for im in ims:
        im["url"], im["file"] = im["src"].split("?")[0], im["files"][0]
        if im["url"] in known:
            im["key"] = known[im["url"]]
    todo = [im for im in ims if "key" not in im] if update else ims
    if update:
        print(f"update: {len(ims) - len(todo)} photos already on the site, {len(todo)} new")
    if "--no-download" not in sys.argv and todo:
        jobs = [(im["src"], f) for im in todo for f in im["files"]]
        done = 0
        with cf.ThreadPoolExecutor(8) as ex:
            for dest, status in ex.map(download_one, jobs):
                done += 1
                if status.startswith("FAILED"):
                    print(status, dest)
                if done % 200 == 0:
                    print(f"downloaded {done}/{len(jobs)}", flush=True)
        print("download finished:", len(jobs), "images")
    if "--no-optimize" not in sys.argv and todo:
        os.makedirs(ASSETS, exist_ok=True)
        with cf.ThreadPoolExecutor(4) as ex:
            keys = list(ex.map(lambda im: optimise(im["file"], im["chart"]), todo))
        for im, k in zip(todo, keys):
            im["key"] = k
        print("optimised", len(todo), "images ->", len(set(keys)), "unique files")
    if all(im.get("key") for im in ims):                                  # drop web copies no product uses any more (products Gioberti removed)
        used = {im["key"] for im in ims}
        gone = [f for f in os.listdir(ASSETS) if re.fullmatch(r"[0-9a-f]{12}(-[ctz])?\.webp", f) and f[:12] not in used]
        for f in gone:
            os.remove(os.path.join(ASSETS, f))
        if gone:
            print("removed", len(gone), "unused web images")
    for it in items:
        by_id = {im["id"]: im.get("key") for im in it["images"]}
        it["colour_img"] = {c: by_id.get(i) for c, i in it["colour_img"].items() if by_id.get(i)}
        for im in it["images"]:
            im.pop("file", None); im.pop("files", None); im.pop("id", None); im.pop("src", None)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(items, open(OUT_JSON, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print("wrote", os.path.relpath(OUT_JSON, ROOT), len(items), "products;", len(skipped), "of them sold out:", ", ".join(skipped))


if __name__ == "__main__":
    main()
