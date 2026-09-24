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
- **Fonts — ONE typeface site-wide:** Cormorant Garamond only (the sole Google Font loaded). `--sans` and `--mono` in `css/style.css` are aliases of `--serif`, so never introduce another family. Because Cormorant is light and small, `html` is 112.5% and small UI text (nav, buttons, labels, tables, forms) gets weight 600–700 in the final "ONE TYPEFACE" block. The Stripe-style labels (`[ bracketed ]` CTAs, underlined small-caps eyebrows) are kept, now set in Cormorant. The rest of the stripe.press experiment (dashed rules, grain, slash-numeral index, floating-model chapter) lives only on the unmerged `editorial-preview` branch.
- **Chess glyphs:** hand-built uniform Staunton-style SVG symbols (king/queen/bishop/knight/rook/pawn) defined inline in each page's `<svg><defs>` block — consistent base/collar/stem proportions modeled on a real Staunton set. Don't reintroduce the old crude/inconsistent glyph shapes.
- **CSS cache-busting:** `css/style.css?v=N` query param on every page — bump `N` on every CSS change and update it across *all* HTML files (`sed` one-liner) **and** `CSS_VERSION` in `tools/gen_pawn_pages.py`, or browsers will serve stale styles. Currently **v=23**.

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
- `gen_home_showcase.py` — builds the homepage showcase. **Adding products:** King → add the product to `tools/catalog/king.json` + photo in `assets/img/products/`, run `make_king_cutouts.py`, `gen_king_page.py`, then this script. Pawn → new colourways appear automatically (after `process_pawn_images.py` / `make_hero_cutouts.py` and listing them in `gen_pawn_pages.py`). Bishop/Rook → add to `OBJECTS` in the script. Queen → add a builder once it has photography.

### Shop system: filters, compare, Quick View + reviews (King + Pawn style pages)
Data-driven so the catalog can grow to hundreds of products without touching JS:
- **King** grid is generated from `tools/catalog/king.json` by `tools/gen_king_page.py` (also feeds the homepage showcase). Each product's `color` / `pattern` / `style` / `occasion` (list) values become sidebar filter groups automatically; groups with <2 distinct values hide themselves. Add a new attribute = add it to the JSON + `FACETS` in `gen_king_page.py`. The current attribute values are first-pass guesses — the user will refine them.
- **Pawn** style pages: each colourway card gets `data-f-color` (family via `COLOR_FAMILY` in `gen_pawn_pages.py`; unknown slugs land in "Other") and `data-f-tone` (Dark/Mid/Light, computed from the cutout). New colourways/lines flow through `gen_pawn_pages.py`.
- Shared markup: `tools/shoplib.py` (`shop_block`). Behaviour: `js/shop.js` (sidebar filters with live counts, chips, sort, mobile drawer, compare tray for up to 3, Quick View dialog). Cards carry `data-id/name/tag/price/img/f-*`. To use it on Bishop/Rook later, generate their cards the same way and load `reviews-data.js` + `shop.js`.
- **Reviews:** `js/reviews-data.js`, keyed by card `data-id` (`king/<slug>`, `pawn/<line>/<colour>`). All entries are **sample placeholders** (`sample:true` shows a "Sample review" tag) — replace with real ones and drop the flag. Reviewer-attribute filters (height, build, size bought, fit, occasion / kids: age…) are built from whichever fields the reviews contain; the field list per category is `REVIEW_FACETS` in the generators. "Write a review" opens a mailto (no backend).
- **Compare the four cuts** table on `pawn.html`: generated from `COMPARE` + `LINES` in `gen_pawn_pages.py` (contents per cut are assumptions — verify).
- **Size chart:** the placeholder charts live in `PAGES["size-guide"]` in `tools/gen_info_pages.py`; the size hints in Quick View are `sizeNote` in `js/shop.js`. The user plans to supply the real chart — replace both.

### Mascot — "Sir Checkmate" (`js/mascot.js`)
Original 3D mascot (glossy inflated gentleman: brass king's crown, monocle, burgundy bow tie) built from primitives with three.js (vendored `js/vendor/three-0.159.module.min.js`, loaded ~1s after page load). He is **small and free-floating, NOT scroll-driven** (the user explicitly asked for that): a 210×250 (150×180 on phones) click-through canvas, moved with a CSS transform along a slow looping sine-wave route that wanders the whole viewport (`route()`), turning to face his direction of travel, banking, bobbing and waving. Skipped for reduced-motion visitors; pauses when the tab is hidden. Tune size in `SIZE()` + `.mascot-canvas`, route/speed in `route()`, look in `buildMascot()`. `window.__mascotFrame(ms)` is a test hook (drive frames by hand when the browser pane is hidden). Created because the user liked a floating 3D figure on stripe.press and wanted an original company character.

### Footer pages & contact
Footer Company/Service links open real pages generated by `tools/gen_info_pages.py` (`our-story`, `master-tailors`, `sustainability`, `press`, `book-a-fitting`, `size-guide`, `alterations`, `shipping-returns` `.html`; hero = the Queen-style glyph `.cat-hero`; styles in the INFO PAGES block of `style.css`). Copy, size charts and policies are placeholder concept copy. Book a Fitting is a form that opens the visitor's email app (`mailto:`), since there is no backend. Contact details everywhere: `suit.shop.dtla@gmail.com`, `+1 (310) 890-6991`, Los Angeles (single LA studio). Privacy/Terms/Accessibility and social icons still link to `#`.

### Announcement bar (`.announce`, every page)
Calm two-part bar (no marquee): rotating promises on the left (Pawn now open / free alterations / free shipping over $500), service links on the right (phone, Size Guide, Book a Fitting); links hide on mobile. Same markup on all 10 pages and in `gen_pawn_pages.py` — change all together.

## Things NOT to redo
- Don't revert to a dark/black overall theme — user explicitly wants light + checkerboard.
- Don't make the exploding-diagram pieces illustrated/sketched again — must be real photography.
- Don't make the exploding-diagram scroll-scrubbed again — it triggers once on scroll-into-view.
- Don't turn the homepage hero back into a static lineup — it is the rotating showcase.
- Don't give the hero models mismatched sizes again — they should be uniform.
- Don't crop category hero images (`object-fit: cover` banners) — show the whole figure.
