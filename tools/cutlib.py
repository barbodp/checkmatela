import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi

def load(path):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return im, np.asarray(im).astype(np.int16)

def make_alpha(arr, near=247, sat=10, pocket_tol=1.8, shadow_band=0.80):
    h, w, _ = arr.shape
    mn = arr.min(axis=2); mx = arr.max(axis=2)
    cand = (mn >= near) & ((mx - mn) <= sat)
    lab, n = ndi.label(cand)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    bgmean = arr[bg].mean(axis=0)
    # enclosed pockets whose colour matches the true background (not white shirt)
    sizes = ndi.sum(cand, lab, index=np.arange(1, n + 1))
    for i, s in enumerate(sizes, 1):
        if i in border or s < 60:
            continue
        m = lab == i
        mean = arr[m].mean(axis=0)
        if np.all(np.abs(mean - bgmean) < pocket_tol):
            bg |= m
        elif s < 1000 and abs(mean[2] - mean[0]) < 1.0 and abs(mean[2] - mean[1]) < 1.0 and mean.min() >= 249:
            bg |= m   # thin neutral slivers between arm and body
    fg = ~bg
    # floor shadow: soft neutral grey that is connected to the background through smooth (low-gradient)
    # pixels. Garment edges are hard steps, so light-grey / white trousers are not eaten.
    y0 = int(h * shadow_band)
    lum = arr.mean(axis=2)
    gy, gx = np.gradient(ndi.gaussian_filter(lum, 1.0))
    smooth = np.hypot(gx, gy) < 2.5
    soft = np.zeros_like(fg)
    soft[y0:] = (((mx - mn) <= 14) & (lum >= 150) & smooth)[y0:]
    seed = ndi.binary_dilation(bg, iterations=1)
    lab_s, _ = ndi.label(soft | bg)
    ids = np.unique(lab_s[seed & (soft | bg)]); ids = ids[ids > 0]
    shadow = np.isin(lab_s, ids) & soft
    fg &= ~shadow
    # keep the largest connected piece only (drops stray specks)
    lab2, n2 = ndi.label(fg)
    if n2 > 1:
        sz = ndi.sum(fg, lab2, index=np.arange(1, n2 + 1))
        fg = lab2 == (1 + int(np.argmax(sz)))
    # fill tiny holes inside the figure
    fg = ndi.binary_fill_holes(fg) | fg
    return fg

def defringe_and_feather(arr, fg, erode=1, sigma=0.8, band=3):
    core = ndi.binary_erosion(fg, structure=np.ones((3, 3)), iterations=erode)
    alpha = ndi.gaussian_filter(core.astype(np.float32), sigma)
    interior = ndi.binary_erosion(core, structure=np.ones((3, 3)), iterations=band)
    idx = ndi.distance_transform_edt(~interior, return_distances=False, return_indices=True)
    rgb_nearest = arr[idx[0], idx[1]]
    edge = core & ~interior
    rgb = arr.copy()
    rgb[edge] = rgb_nearest[edge]
    rgba = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
    return Image.fromarray(rgba, "RGBA")

def cutout(path, **kw):
    im, arr = load(path)
    fg = make_alpha(arr, **kw)
    out = defringe_and_feather(arr, fg)
    bbox = out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    return out.crop(bbox)

def preview(img, bgcolor=(70, 120, 100)):
    bg = Image.new("RGBA", img.size, bgcolor + (255,))
    return Image.alpha_composite(bg, img).convert("RGB")


def keep_largest_alpha(img, threshold=8):
    """Drop stray fragments: keep only the largest connected piece of an RGBA cutout."""
    a = np.asarray(img.getchannel("A")) > threshold
    lab, n = ndi.label(a)
    if n <= 1:
        return img
    sizes = ndi.sum(a, lab, index=np.arange(1, n + 1))
    keep = lab == (1 + int(np.argmax(sizes)))
    out = np.asarray(img).copy()
    out[~keep, 3] = 0
    return Image.fromarray(out, "RGBA")
