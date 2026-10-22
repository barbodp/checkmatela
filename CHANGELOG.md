# Checkmatela changes

## 2026-10-22 — Men's casual shirts: fewer plaids, one page per shirt

- The plaid and pearl snap shirts were 8 listings with 340+ colourways (many near-identical, many with 1–2 sizes left). Now 3 listings, each one page with a Sleeve choice: **Men's Plaid Shirt** (12 plaids), **Men's Plaid Pearl Snap Western Shirt** (12 plaids) and **Men's Solid Pearl Snap Western Shirt** (13 solids, Gioberti's best seller). Plaids chosen for stock depth in both sleeves and distinct colours. Old pages redirect to the new ones.
- Every product page shows the chosen colour (name + swatch); choosing a sleeve shows that version's photo.

## 2026-10-22 — Categories combine every brand

- Each Formal category is now one page with every brand: Men's **Suits** (93 Antonio Uomo) and **Tuxedos** (41) are new category pages; Blazers and Dress Pants keep Gioberti + Antonio Uomo together. Kids' **Suits & Blazers**, new **Tuxedos**, **Suit Vests** and **Dress Pants** now include the Magen Kids pieces (regular and husky) next to Gioberti's. Brand and Fit filters on every category page.
- Magen Kids pieces have their own product pages (photos, size dropdown, what's included), like the other brands.
- The Formal menus link to the combined pages; brand pages stay under Brands. Hidden Gioberti helper items (a "$1 additional price" add-on) are skipped by the stock sync.

## 2026-10-21 — Automatic Gioberti stock sync, tidier categories

- Stock, prices and products now refresh from gioberti.com every 3 hours (GitHub Actions, `.github/workflows/gioberti-stock.yml`): sold-out colours/sizes/products and restocks update on their own; changes publish only when something changed.
- Men: Jackets and Outerwear merged into **Jackets & Outerwear** (old Outerwear link redirects); sweaters Gioberti filed under Outerwear/Hoodies moved to Sweaters; the fleece hoodie moved to Hoodies; Accessories renamed **Accessories & Footwear** (it has sandals). Filing is rule-based, so new products follow the same rules.

## 2026-10-20 — Gioberti catalog, Formal / Not So Formal for Men and Boys

- Added the whole **Gioberti** catalog (gioberti.com, dropship supplier): 189 in-stock products, each with its own page (photos, colour and size pickers with sold-out combinations disabled, the photo follows the colour, price, details and that product's own size chart). Sold-out products and the gift card are left out.
- **Men and Boys now split by dress code.** *Formal* keeps the existing suits, tuxedos (Antonio Uomo, Magen Kids) and adds Blazers & Sport Coats, Suit Vests & Vest Sets, Dress Shirts and Dress Pants. *Not So Formal* is new and copies Gioberti's own categories (Casual Shirts, Flannel, Polos, Sweaters, Hoodies, Jackets, Outerwear, Leather Jackets, Activewear, Sleepwear, Casual Shorts, Accessories). Landing pages: `men-formal.html`, `men-not-so-formal.html`, `boys-formal.html`, `boys-not-so-formal.html`; one page per category (`men-*.html`, `boys-*.html`).
- Formal accessories (cummerbund and suspender sets) went into the existing Accessories page (`bishop.html`).
- **Menus:** Men and Kids panels (and the phone menu) now show three closed dropdowns — Formal, Not So Formal, Occasion — listing categories only.
- King and Pawn landing pages got a Formal / Not So Formal category bar under the intro. Every new product is in site search.
- Prices are Gioberti's listed prices, copied as placeholders — set the real markup before selling.
- New tools: `tools/gb_fetch.py` (catalog + photos) and `tools/gen_gioberti.py` (pages); `gen_nav.py` indexes them.

## 2026-09-28 — Event-first customer messaging

**Pre-change production snapshot:** [`codex/pre-customer-messaging-2026-09-28`](https://github.com/barbodp/checkmatela/tree/codex/pre-customer-messaging-2026-09-28) (commit `f5e8b94`). This branch preserves the exact `main` version before the changes below.

- Reframed the homepage and collections around occasions, dress codes, fit and event timing while retaining the existing design and chess identity.
- Added **Find Your Look**, a three-choice guide that points visitors to a relevant collection and carries their interest into a fit enquiry.
- Rewrote fit, tailoring, alterations, shipping and brand pages to answer buying questions and state the site's current preview status accurately.
- Added clear next steps on product views and the preview bag; saved pieces are included in an enquiry draft.
- Removed fabricated testimonials and sample reviews, unverified service guarantees and invented business statistics from customer-facing pages.
- Kept the price, size and checkout demonstrations visible with clear labels that they are illustrative and cannot currently take an order.

The site is still a static collection preview. Checkout, inventory, service terms and email capture require real operations and integrations before customer sales can be accepted.
