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
- **CSS cache-busting:** `css/style.css?v=N` query param on every page — bump `N` on every CSS change and update it across *all* HTML files (`sed` one-liner) **and** `CSS_VERSION` in `tools/gen_pawn_pages.py`, or browsers will serve stale styles. Currently **v=29**. `css/style.css` is one long file made of appended blocks — when replacing a block, replace only that block's span (an earlier slicing edit once deleted the blocks after it).

## Site architecture

- `index.html` — homepage:
  - **Board hero** (`#heroBoard`, `js/hero-board.js`, `css/hero-board.css`): an interactive **3D chessboard** where the pieces are the navigation — a full standard 32-piece setup (white clickable, black = the opponent's side), polished marble squares in a walnut frame with a  glossy piano-black / silvery-ivory lacquer pieces, reflections in the board, soft contact shadows, dark studio look (the user's reference photo). Hover = lift + brass ring + label; click = the piece makes its own chess move, camera dives, page dissolves, then navigates (King→king, Queen→queen, Pawn→pawn, Bishop→bishop, Rook→rook, Knight→book-a-fitting). A key row under the board mirrors the pieces as real links (keyboard/touch/no-WebGL/reduced-motion fallback). Test hook `window.__hb`. Details in the "Hero board" section below.
  - **Product carousel** (the old rotating hero) was removed from the live homepage at the user's request but is fully recoverable: git tag `homepage-carousel-v1` is the whole previous homepage; or run `tools/gen_home_showcase.py` (fills the empty `<!-- SHOWCASE:START/END -->` slot below the hero) and add `<script src="js/showcase.js"></script>` to `index.html`.
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
Original 3D mascot (glossy inflated gentleman: brass king's crown, monocle, burgundy bow tie) built from primitives with three.js (vendored `js/vendor/three-0.159.module.min.js`, loaded ~1s after page load). **Small, free-floating, NOT scroll-driven and not confined to the hero** (user's explicit asks): a 210×250 (150×180 on phones) click-through canvas, moved with a CSS transform, that **sweeps diagonally across the screen** — enters below the bottom edge, crosses 55–95% of the width in a lazy S-curve while rising, dissolves near the top, rests 1–2.5 s, then sweeps back the other way (bottom-left→top-right, then bottom-right→top-left, random start/width each time; ~17–23 s per sweep) — so over time he covers the whole homepage at any scroll position. Turns to face his direction of travel, banks, waves. **Groove:** a soft beat (~2.4 s, `GROOVE` constants) pulses his forward speed (surge/glide), lifts him in a small hop, and times a slight squash-and-stretch, head nod and arm/leg swing — deliberately subtle ("the slightest groove"). Pace/pauses/crossing/sway are the `RISE` constants, size is `SIZE()` + `.mascot-canvas`, look is `buildMascot()`. Skipped for reduced-motion; pauses when the tab is hidden. Test hooks: `window.__mascotFrame(ms)` drives a frame; `window.__mascotSeek(sec)` fast-forwards his clock (handy when the browser pane reports the page as hidden and never runs animation frames). Created because the user liked a floating 3D figure on stripe.press and wanted an original company character.

### Hero board (live homepage hero)
Files: `js/hero-board.js` (three.js, vendored in `js/vendor`), `css/hero-board.css`, the `.hero-board` section in `index.html`. **Look = the user's reference photo: dark, clean, glossy, realistic.** Standard starting position, all 32 pieces (`WHITE`/`BLACK` built from `BACK`); all white pieces are clickable (hover any → matching key lights up). **Pieces = real stone, matching the user's third reference photo (luxury-interior travertine + black chess set): white = honed cream TRAVERTINE (porous, elongated pits/voids along the bedding, soft strata, satin-matte, strong bump), black = POLISHED BLACK STONE (deep, glossy, faint mottling).** Accurate turned geometry, no flat primitives (`buildPiece`): stepped ribbed foot, incised rings, ball-headed pawn, crenellated rook, mitred bishop with a cut, beaded-crown queen, king with a carved extruded cross, smooth carved knight head with ears. Procedural textures `travertineCanvas` / `blackStoneCanvas`; each piece gets its own random slice of the stone so no two pieces share the same pits. **Board = chunky travertine slab edge, honed travertine light squares, polished black-stone squares (only those are see-through, mirroring the pieces).** History: the pieces went lacquer → faceted carved → raw wood → stone at the user's direction; the user prizes realism and 'exact material style' from their reference photos. Don't add brass/gilding or ornament that isn't in the references. Test hooks `__hb.zoom(type, k, fov)` / `unzoom()` magnify a piece. Board realism: procedural marble squares (`marbleCanvas`), walnut frame texture (`woodCanvas`),  see-through squares with upside-down "twin" pieces as reflections (`addMirror`, hidden at the sides by a dark skirt), radial contact shadows, dark studio env with strip lights, low 29° camera, scene fog. Each type's move is in `MOVES` (landing squares are empty ranks 3-6; back-rank pieces hop over the pawns). Test hook `window.__hb` (advance/click/hover/noNav; chained tweens need `await Promise.resolve()` between `advance` calls). The user liked it "clean, glossy, realistic" and wanted the opponent's side visible "how a chess board is properly set up" — don't go back to the sparse scenery layout. Ideas the user may still choose from: occasion "openings" recommending suits, Sir Checkmate playing, colourway pieces, attract-mode game, sound.

**Dark hero on category pages:** `.cat-hero` (King, Queen, Pawn + its four style pages, Bishop, Rook, footer info pages) uses the homepage's dark studio look, with the models/products standing on a **brightly lit black-and-white chessboard stage** in front of the dark room (perspective checker stage `.cat-hero__bg`, spotlight pool + top light cone `.cat-hero::before`, walnut-and-brass front lip `.cat-hero::after`, reflection under the figures, ivory/brass type). Only the hero was changed; the rest of those pages is still ivory — the user said they will work on the product pages' look separately later.

**Queen page** (`queen.html`) is intentionally a working but blank page (header, glyph hero, one-line empty state, footer) — no waitlist/marketing — until Queen products exist.

### Footer pages & contact
Footer Company/Service links open real pages generated by `tools/gen_info_pages.py` (`our-story`, `master-tailors`, `sustainability`, `press`, `book-a-fitting`, `size-guide`, `alterations`, `shipping-returns` `.html`; hero = the Queen-style glyph `.cat-hero`; styles in the INFO PAGES block of `style.css`). Copy, size charts and policies are placeholder concept copy. Book a Fitting is a form that opens the visitor's email app (`mailto:`), since there is no backend. Contact details everywhere: `suit.shop.dtla@gmail.com`, `+1 (310) 890-6991`, Los Angeles (single LA studio). Privacy/Terms/Accessibility and social icons still link to `#`.

### Announcement bar (`.announce`, every page)
Calm two-part bar (no marquee): rotating promises on the left (Pawn now open / free alterations / free shipping over $500), service links on the right (phone, Size Guide, Book a Fitting); links hide on mobile. Same markup on all 10 pages and in `gen_pawn_pages.py` — change all together.

## Things NOT to redo
- Don't revert to a dark/black overall theme — user explicitly wants light + checkerboard.
- Don't make the exploding-diagram pieces illustrated/sketched again — must be real photography.
- Don't make the exploding-diagram scroll-scrubbed again — it triggers once on scroll-into-view.
- Don't turn the homepage hero back into a static lineup — it is the interactive 3D board (the carousel is archived under tag `homepage-carousel-v1`).
- Don't give the hero models mismatched sizes again — they should be uniform.
- Don't crop category hero images (`object-fit: cover` banners) — show the whole figure.
