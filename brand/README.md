# Checkmatela logo family

A single identity built around the floating Sir Checkmate mascot: king crown, monocle, smile, tuxedo, burgundy bow tie, and pine detail. The marks share one drawing and one wordmark; formats change only to fit each use.

## Choose a file

| Use | Master asset | Raster export |
| --- | --- | --- |
| Main marketing lockup | `svg/primary-horizontal.svg` | `png/primary-horizontal.png` |
| On a dark pine field | `svg/primary-horizontal-reverse.svg` | `png/primary-horizontal-reverse.png` |
| Website header / narrow placements | `svg/compact-horizontal.svg` | `png/compact-horizontal.png` |
| Website footer / dark narrow placements | `svg/compact-horizontal-reverse.svg` | `png/compact-horizontal-reverse.png` |
| Centered layouts | `svg/stacked.svg` | `png/stacked.png` |
| Postcard, sticker, stamp, social avatar | `svg/seal.svg` | `png/seal.png` |
| Symbol only | `svg/symbol-color.svg` | `png/symbol-color.png` |
| One color print or embroidery | `svg/symbol-one-color.svg` | `png/symbol-one-color.png` |
| Wordmark only | `svg/wordmark.svg` | `png/wordmark.png` |
| Browser tab and app tile | `svg/favicon.svg` | `png/favicon.png` |

The SVG wordmark and tagline are **outlined paths**. They remain consistent without installed fonts. SVGs are the masters for print and scaling; PNGs are transparent except for the reverse lockups and favicon.

## Print and spacing

The `examples/` folder includes editable 6 × 4 inch postcard fronts and backs, plus 1800 × 1200 PNGs tagged at 300 dpi. Add bleed according to the printer's specification before sending to press. Leave clear space around the full logo equal to at least half the mascot's head width. Prefer a 40 mm or larger seal so the monocle and bow tie remain legible. Use the simplified favicon at very small sizes.

## Colors

- Pine `#0F2E22` — identity field and wordmark
- Ink `#15181A` — tuxedo and contrast
- Paper `#FAF8F2` — warm neutral base
- Brass `#AD7F3C` — crown and details
- Burgundy `#7A2036` — bow tie

## Source and export

The `source/` folder contains the drawing builder, outlined letter paths, Swift outline utility, and raster export scripts. Run `python3 brand/source/build.py`, then `node brand/source/export.js` from the repository root. The Node exporter uses the Codex workspace's Sharp library path and can be adjusted for another machine.
