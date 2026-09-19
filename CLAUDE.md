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
- **CSS cache-busting:** `css/style.css?v=N` query param on every page — bump `N` on every CSS change and update it across *all* HTML files (`sed` one-liner), or browsers will serve stale styles.

## Site architecture

- `index.html` — homepage:
  - **Board scene**: hero copy + a lineup of 5 uniform-size model photos + the 5 category cards, all sharing one continuous checkerboard background/fade (not separate sections) — this was an explicit redesign, don't split it back apart.
  - **Exploding suit diagram** (`#diagram`): real studio product photography (not illustrations) for jacket/shirt/trousers/shoes/bow tie/pocket square/cufflinks, laid out in fixed "worn" anatomical positions (neck/shoulders/waist/legs/feet, symmetric left-right pairs), explodes via IntersectionObserver-triggered CSS transform (no scroll-scrubbing) the moment the section scrolls into view. Pieces are real photos in `assets/img/diagram/`.
  - Featured product grid, brand story, quotes, newsletter, footer.
- `king.html`, `queen.html`, `pawn.html`, `bishop.html`, `rook.html` — the five category pages.
- `pawn-suit-vest-set.html`, `pawn-tuxedo-vest-set.html` — live Pawn subcategory pages with a gallery product grid (see below).
- `css/style.css`, `js/main.js` — shared across every page.
- `assets/img/` — `hero/` (model cutouts), `products/`, `categories/`, `details/`, `diagram/` (+ `diagram_raw/` originals), `pawn/` (kids product photography).

### Category naming (chess piece ↔ department)
- **King** = Men (full product catalog, live)
- **Queen** = Women (fully "Coming Soon" — no product photography exists yet)
- **Pawn** = Kids (partially live — see below)
- **Bishop** = Accessories (live, uses AI-generated studio product photography)
- **Rook** = Shoes (live, uses AI-generated studio product photography)

### Pawn subcategories (current status)
Pawn has 4 style dropdown/grid entries on `pawn.html` ("Shop by Style"):
- **Suit Vest Set** — LIVE → `pawn-suit-vest-set.html`. 4 colorways (Black, Indigo, Light Gray, Navy), $89. Source photography from `/Users/barbodp/Downloads/Magen Kids/Suit Vest Set/`.
- **Tuxedo Vest Set** — LIVE → `pawn-tuxedo-vest-set.html`. 4 colorways (Black, Burgundy, Light Gray, Light Navy), $99. Source photography from `/Users/barbodp/Downloads/Magen Kids/Tuxedo Vest Set/`.
- **Slim Fit** — still "Coming Soon" (no photography supplied yet).
- **Tuxedo** (without vest) — still "Coming Soon" (no photography supplied yet).

The main nav has a hover dropdown under "Pawn — Kids" (all pages) linking directly to these four; on mobile it's a static inline list instead of hover.

### Gallery product cards (`.gallery-card`, used on the two live Pawn pages)
Each colorway shows a main image + a 6-thumbnail strip, **in this fixed order: 4 model shots, then 2 plain/product-only shots** (`model-1..4.jpg`, then `plain-1..2.jpg`). Clicking a thumbnail swaps the main image (see `.gallery-card` JS in `main.js`). Follow this same pattern (models-then-plain) if more real product photography gets added later.

### Processed image naming convention
When new raw product photography comes in (e.g. under `~/Downloads/...`), process it into `assets/img/pawn/<line-slug>/<color-slug>/model-N.jpg` + `plain-N.jpg` (resize to ~900px max width, JPEG quality ~84, strip alpha onto white) rather than committing the raw multi-MB originals.

## Things NOT to redo
- Don't revert to a dark/black overall theme — user explicitly wants light + checkerboard.
- Don't make the exploding-diagram pieces illustrated/sketched again — must be real photography.
- Don't make the exploding-diagram scroll-scrubbed again — it triggers once on scroll-into-view.
- Don't give the hero models mismatched sizes again — they should be uniform.
