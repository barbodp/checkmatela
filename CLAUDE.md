# Checkmatela

A chess-themed formal wear e-commerce concept site. Static HTML/CSS/JS, no build step, no framework, no backend — every page is opened/served as-is.

- **Local path:** `/Users/barbodp/Suit Business`
- **GitHub:** https://github.com/barbodp/checkmatela (branch `main`)
- **Live site:** https://checkmatela.vercel.app

## Workflow (always follow this)

1. Make changes locally.
2. `git add -A && git commit -m "..."` — every meaningful round of changes gets its own commit. Keep the full version history in git; don't squash/rewrite it.
3. `git push origin main`.
4. That's it — **Vercel is linked to the GitHub repo and auto-deploys `main` to production on every push.** Do not run manual `vercel --prod` deploys for routine changes.

### Local tooling note
This machine has no Homebrew. `gh`, `node`/`npm`, and the `vercel` CLI were installed as standalone binaries (not on PATH by default):
- `gh` → `~/.local/bin`
- `node`/`npm`/`npx` → `~/.local/node/bin`
- `vercel` global npm package → installed into `~/.local/node` prefix, also picked up via `~/.local/node/bin`
- Vercel CLI auth lives at `~/.local/vercel-config` (pass `--global-config "$HOME/.local/vercel-config"` or `export VERCEL_GLOBAL_CONFIG_DIR=...`)
- `gh auth setup-git` has already been run, so plain `git push`/`git pull` authenticate fine with no extra steps.

To use these tools in a fresh shell:
```bash
export PATH="$HOME/.local/node/bin:$HOME/.local/bin:$PATH"
export VERCEL_GLOBAL_CONFIG_DIR="$HOME/.local/vercel-config"
```

## Design system

- **Theme:** light/ivory base (`--paper`) with a real black-and-white checkerboard motif (hero, footer strip, category banners) — not the dark theme it started as.
- **Palette:** pine green `--pine` (primary accent, buttons, links), brass/gold `--brass` (metallic accent), burgundy `--burgundy` (jewel accent, prices, swatches). Full token list at the top of `css/style.css`.
- **Fonts:** Cormorant Garamond (serif, display/headings) + Jost (sans, UI/body), via Google Fonts.
- **Chess glyphs:** hand-built uniform Staunton-style SVG symbols (king/queen/bishop/knight/rook/pawn) defined inline in each page's `<svg><defs>` block — consistent base/collar/stem proportions modeled on a real Staunton set. Don't reintroduce the old crude/inconsistent glyph shapes.
- **CSS cache-busting:** `css/style.css?v=N` query param on every page — bump `N` on every CSS change and update it across *all* HTML files (`sed` one-liner) **and** `CSS_VERSION` in `tools/gen_pawn_pages.py`, or browsers will serve stale styles. Currently **v=14**.

## Site architecture

- `index.html` — homepage:
  - **Showcase hero** (`#showcase`, generated): a rotating product carousel on a light checkerboard — copy on the left, full-figure cutouts standing on a chip/controls bar on the right. Slides interleave King (every suit in `king.html`), Pawn (4 lines, colourway swatches auto-cycle inside the slide), Bishop (3 accessories) and Rook (shoes), after a welcome slide with the `<h1>` "Every move, tailored.". Transition is a **chessboard wipe** (dark/light squares scale in and out diagonally) with staggered text and figures; auto-advances via a CSS progress line (pauses on hover/focus/hidden tab/off-screen), category chips, arrows, swipe and arrow keys, `prefers-reduced-motion` = crossfade. Markup lives between `<!-- SHOWCASE:START/END -->` in `index.html` and is written by `tools/gen_home_showcase.py`; behaviour is `js/showcase.js`. **Don't hand-edit that block — re-run the generator.**
  - Under it: the trust strip and a compact "Shop by piece" category row (`.categories`, five cards on plain ivory). The old 5-model lineup + big checker area was removed on purpose (user: too much empty space) — don't bring it back.
  - **Exploding suit diagram** (`#diagram`): real studio product photography (not illustrations) for jacket/shirt/trousers/shoes/bow tie/pocket square/cufflinks, laid out in fixed "worn" anatomical positions (neck/shoulders/waist/legs/feet, symmetric left-right pairs), explodes via IntersectionObserver-triggered CSS transform (no scroll-scrubbing) the moment the section scrolls into view. Pieces are real photos in `assets/img/diagram/`.
  - Featured product grid, brand story, quotes, newsletter, footer.
- `king.html`, `queen.html`, `pawn.html`, `bishop.html`, `rook.html` — the five category pages.
- `pawn-slim-fit.html`, `pawn-suit-vest-set.html`, `pawn-tuxedo.html`, `pawn-tuxedo-vest-set.html` — the four live Pawn subcategory pages, each a gallery product grid (see below).
- `tools/` — the Python scripts that generate the Pawn pages and the image assets (see "Tools" below).
- `css/style.css`, `js/main.js` — shared across every page.
- `assets/img/` — `hero/` (model cutouts), `products/`, `categories/`, `details/`, `diagram/` (+ `diagram_raw/` originals), `pawn/` (kids product photography).

### Category naming (chess piece ↔ department)
- **King** = Men (full product catalog, live)
- **Queen** = Women (fully "Coming Soon" — no product photography exists yet)
- **Pawn** = Kids (live — four style pages, see below)
- **Bishop** = Accessories (live, uses AI-generated studio product photography)
- **Rook** = Shoes (live, uses AI-generated studio product photography)

### Pawn subcategories (current status — all four are LIVE)
`pawn.html` is the landing page ("Shop by Style" dropdown + four photo cards). Each style has its own page:
- **Slim Fit** → `pawn-slim-fit.html` — 14 colorways, $129. Source: `~/Downloads/Magen Kids/Slim Fit/`.
- **Suit Vest Set** → `pawn-suit-vest-set.html` — 4 colorways, $89. Source: `~/Downloads/Magen Kids/Suit Vest Set/`.
- **Tuxedo** (style TX-1026) → `pawn-tuxedo.html` — 12 colorways, $139. Source: `~/Downloads/Magen Kids/Tuxedo TX-1026/`.
- **Tuxedo Vest Set** → `pawn-tuxedo-vest-set.html` — 4 colorways, $99. Source: `~/Downloads/Magen Kids/Tuxedo Vest Set/`.

Prices are invented placeholders (the concept site has no real pricing) — tell the user if asked.
The main nav has a hover dropdown under "Pawn — Kids" (all pages) linking to the four pages; on mobile it's a static inline list.

The four Pawn style pages are **generated** by `tools/gen_pawn_pages.py` (they are near-identical) — edit the generator and re-run it rather than hand-editing the four files (colour lists, prices, intro copy and hero figures live in its `LINES` config). Its `CSS_VERSION` must match the `?v=N` on the other pages.

### Gallery product cards (`.gallery-card`, used on the four Pawn style pages)
Each colorway shows a main image + a thumbnail strip, **in this fixed order: 4 model shots, then the plain/product-only shots** (`model-1..4.jpg`, then `plain-1..2.jpg`; a few colorways only have 1 plain shot). The strip uses small `thumb-N.jpg` files (160px squares) while `data-src` points at the full 900px image; clicking swaps the main image (see `.gallery-card` JS in `main.js`). Follow this same pattern (models-then-plain) if more real product photography gets added later.

### Processed image naming convention
When new raw product photography comes in (e.g. under `~/Downloads/...`), process it into `assets/img/pawn/<line-slug>/<color-slug>/model-N.jpg` + `plain-N.jpg` + `thumb-N.jpg` (mains ~900px max width, JPEG quality ~82, alpha flattened onto white; thumbs 160px squares — models cropped from the top, plain shots from ~30% down) rather than committing the raw multi-MB originals. Raw files use inconsistent names (case, spaces, missing `_1`/`_2`), so glob per folder instead of building filenames.

### Category heroes (`.cat-hero`)
Every category page (King, Queen, Pawn landing, the four Pawn style pages, Bishop, Rook) uses the same hero: a **light checkerboard scene** (same board as the homepage) with copy in a frosted plate on the left and **full-figure transparent cutouts standing on the bottom edge** on the right — nothing may be cropped (the old dark banner cropped the models at the waist; the user explicitly asked for whole figures). Variants: default = row of uniform-height standing figures (they shrink together to fit, bottom-aligned), `--objects` (Bishop still-life: bow tie, cufflinks, pocket square), `--single` (Rook: shoes), `--glyph` (Queen: large translucent queen piece while there is no photography). The old `.page-banner` CSS is now unused.
- Cutouts are WebP with alpha: kids at `assets/img/pawn/<line>/<colour>/hero.webp`, men/accessories/shoes at `assets/img/hero/cat-*.webp`.
- Every Pawn colourway now has a `hero.webp` cutout (`make_hero_cutouts.py` iterates `process_pawn_images.LINES`, so new colourways are cut automatically). Light/white colourways work because `cutlib` only removes the floor shadow if it is soft grey *connected to the background through smooth (low-gradient) pixels*. Regenerate hero figures on a category page by listing the colour in `hero=[...]` in `tools/gen_pawn_pages.py`.

### Tools (`tools/`)
Run from the repo root; they need `pip install --user pillow numpy scipy` (numpy/scipy are only for the cutouts).
- `process_pawn_images.py` — raw `~/Downloads/Magen Kids/...` → `assets/img/pawn/.../{model,plain,thumb}-N.jpg`.
- `make_hero_cutouts.py` (+ `cutlib.py`) — background removal for the hero figures. The kid photos are AI-style renders on a noisy near-white background; white shirts must survive, so it flood-fills only *neutral, near-white* pixels connected to the border, then also removes enclosed background pockets (between arm and torso) whose colour matches the true background (shirt whites are slightly tinted), strips floor shadows, defringes and feathers the edge.
- `gen_pawn_pages.py` — regenerates the four Pawn pages from the processed images (import-safe; also owns the shared announcement-bar HTML, kept in sync by hand across pages).
- `make_king_cutouts.py` — cuts every `assets/img/products/*.jpg` (men's studio shots) into `assets/img/king/<name>.webp` for the showcase.
- `gen_home_showcase.py` — builds the homepage showcase. **Adding products:** King → add the card to `king.html` + photo in `assets/img/products/`, run `make_king_cutouts.py`, then this script. Pawn → new colourways appear automatically (after `process_pawn_images.py` / `make_hero_cutouts.py` and listing them in `gen_pawn_pages.py`). Bishop/Rook → add to `OBJECTS` in the script. Queen → add a builder once it has photography.

### Announcement bar (`.announce`, every page)
Calm two-part bar (no marquee): rotating promises on the left (Pawn now open / free alterations / free shipping over $500), service links on the right (phone, Size Guide, Book a Fitting); links hide on mobile. Same markup on all 10 pages and in `gen_pawn_pages.py` — change all together.

## Things NOT to redo
- Don't revert to a dark/black overall theme — user explicitly wants light + checkerboard.
- Don't make the exploding-diagram pieces illustrated/sketched again — must be real photography.
- Don't make the exploding-diagram scroll-scrubbed again — it triggers once on scroll-into-view.
- Don't turn the homepage hero back into a static lineup — it is the rotating showcase.
- Don't give the hero models mismatched sizes again — they should be uniform.
- Don't crop category hero images (`object-fit: cover` banners) — show the whole figure.
