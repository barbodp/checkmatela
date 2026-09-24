# Checkmatela

A static, chess-inspired formal wear concept. Open `index.html` directly or serve this directory with a local web server. No framework, build step, account service, or checkout is required.

## Experience

- Five departments: King (men), Queen (women, coming soon), Pawn (kids), Bishop (accessories), and Rook (shoes).
- A continuous checkerboard homepage with five full-length model figures.
- Seven photographic suit components animate apart when the diagram enters view; each links to its department. The control reassembles the look. Reduced-motion preferences are respected.
- 10 men's styles, 34 kids' colorways, and 4 accessory/footwear concepts.
- Product search, quick views, sample size selection, sorting, and a sample bag saved in browser storage. No orders or payments are processed.
- Kids' galleries show four model views before the product-only views.
- Email forms demonstrate validation and a preview confirmation. They do not store or submit addresses.

## Content and imagery

Men's and kids' images are prepared from the supplied Antonio Uomo and Magen Kids folders. Existing AI-generated component, accessory, and shoe imagery illustrates the concept. All prices and sizes are illustrative. The site does not assert actual inventory or live services.

## Updating generated content

1. Edit the Pawn collection configuration in `tools/gen_pawn_pages.py`.
2. Run `python3 tools/gen_pawn_pages.py` to rebuild all four kids' pages.
3. Run `python3 tools/gen_catalog.py` to update the shared browser catalog and accessory/footwear cards. Men's catalog entries are read from `king.html`.

The Pawn generator reads the shared header, announcement, and footer from `tools/partials/`. When changing those shared elements, update the six authored pages as well. Bump the CSS cache version in all HTML pages and `CSS_VERSION` in the Pawn generator after CSS changes. Keep the script cache versions consistent too.

## Publishing

Commit each meaningful change and push `main` to the connected GitHub repository. Vercel deploys automatically; no manual production deployment is needed.
