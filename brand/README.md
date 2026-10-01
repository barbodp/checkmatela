# Checkmatela identity system — The Lifted Square

The core logo pairs an outlined editorial wordmark with a custom **C** monogram. One brass square sits just beyond the letter's opening: a chessboard square in motion, with a subtle nod to the floating character on the site. The character can continue to appear in campaigns and on the website; the logo stays crisp on labels, postcards, and small screens.

Every lockup uses the same letterforms, monogram, square position, and restrained palette. Choose the format that fits the space without redrawing the mark.

## Choose a file

| Use | Master asset | Raster export |
| --- | --- | --- |
| Main marketing lockup, with tagline | `svg/primary-horizontal.svg` | `png/primary-horizontal.png` |
| Main lockup on pine | `svg/primary-horizontal-reverse.svg` | `png/primary-horizontal-reverse.png` |
| Website header and narrow layouts | `svg/compact-horizontal.svg` | `png/compact-horizontal.png` |
| Website footer and dark narrow layouts | `svg/compact-horizontal-reverse.svg` | `png/compact-horizontal-reverse.png` |
| Centered layouts | `svg/stacked.svg` | `png/stacked.png` |
| Sticker, stamp, or large social avatar | `svg/seal.svg` | `png/seal.png` |
| Monogram only | `svg/symbol-color.svg` | `png/symbol-color.png` |
| Single-ink print or embroidery | `svg/symbol-one-color.svg` | `png/symbol-one-color.png` |
| Wordmark only | `svg/wordmark.svg` | `png/wordmark.png` |
| Browser tab and app tile | `svg/favicon.svg` | `png/favicon.png` |

The SVGs are the scaling and print masters. All lettering is outlined, so its appearance does not depend on installed fonts. PNG logo exports are transparent; the favicon has a solid pine background.

## Color and use

- Pine `#0F2E22` — primary wordmark and identity field
- Paper `#FAF8F2` — warm background and reverse lettering
- Brass `#AD7F3C` — lifted square and fine details
- Ink `#15181A` — supporting copy

Keep a clear area around any logo at least the width of the brass square in that lockup. Use the compact version wherever the tagline would become too small to read. Use the favicon or monogram at icon sizes. Do not rotate the square, add a drop shadow, or change the spacing between it and the C. The reverse SVGs have transparent backgrounds and are intended for a solid dark field.

## Postcard files

`examples/postcard-front.svg` and `examples/postcard-back.svg` are editable 6 × 4 inch compositions. Matching 1800 × 1200 pixel PNGs are tagged at 300 dpi. Give the printer the SVG or PNG and add the bleed their specifications require. The postcard copy and URL are examples to customize before printing.

## Source

`source/` contains the vector builder, outlined type paths, and export scripts. To regenerate the package from the repository root, run `python3 brand/source/build.py`, then `node brand/source/export.js`; run the example and board builders for the marketing previews. The raster exporters depend on Sharp and may need their library path adjusted on another machine.
