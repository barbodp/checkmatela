# Raw stone edition — V2

## Versions

- `/hero-stone-v1.html` preserves the approved five-piece stone study with independent CSS, JavaScript, and copied texture/preview assets under `stone-v1`. Only the title and comparison navigation differ from the approved sample.
- `/hero-stone-v2.html` is the enhanced complete chess set. Its code, styling, material maps and preview are separate from V1.
- `/hero-stone.html` and the original wood sample remain as previously published.

## Changes in V2

Raw, warmer grey-beige travertine and weathered charcoal basalt, with fine pores and mineral variation. Materials remain matte and nonmetallic. Actual surface geometry includes fluted stems, softened contours, stepped feet, an open six-leaf queen's crown, closed rook battlements, diagonal bishop cuts, and carved knights with paired ears, cheeks and facial details. Geometry is shared across piece instances; texture placement varies by position. Rendering occurs only when the view changes, without idle animations.

All 32 pieces occupy the standard starting position. White is on ranks 1–2, Black on ranks 7–8. The back rank is rook, knight, bishop, queen, king, bishop, knight, rook from a through h. h1 is light, a1 dark. Both queens stand on their own color. `js/stone-layout-v2.js` is the placement source; `node tools/verify_stone_layout.mjs` compares it against the standard starting FEN and verifies counts, square uniqueness and orientation.

Every piece is clickable: King → Men; Queen → Women (coming soon); Pawn → Kids; Bishop → Accessories; Rook → Shoes; Knight → Book a fitting. Drag and arrow keys rotate; plus/minus zoom; Home resets. Overhead shows the layout. Closer look isolates a selected piece in either material. The static preview and HTML category links provide a fallback without WebGL or JavaScript.

## Generated assets

Created with the built-in image-generation tool on 2026-09-24. These are synthetic photographic texture maps, not scans of a physical chess set. JPEG conversions are stored here. `board-preview.jpg` is a render of the actual interactive scene, not a generated illustration.

### Exact prompt — raw-travertine.jpg

Use case: product-mockup. Asset type: seamless photographic PBR albedo texture for actual 3D carved chess pieces. Square flat high resolution orthographic scan, entire image filled edge-to-edge with raw unsealed grey beige travertine limestone. Natural earthy mushroom, putty, warm mineral grey and quiet taupe; noticeably less cream and yellow than commercial polished travertine. Fine fossil fragments, tiny scattered organic cavities and occasional elongated pores, sparse muted rust mineral flecks, subtle sediment layering, tactile chalk dust. Beautiful restrained organic irregularity, visible grain at macro scale, cavities have neutral taupe interiors. Plausible 20cm area. Matte freshly carved natural stone, not shiny, not painted, no deliberate geometric pattern. Seamless texture with even diffuse lighting, no shadows or lighting gradient or objects or writing or borders. Photorealistic, detailed enough for extreme close-up of stone sculpture. Do not show a chess piece, just the flat stone texture.

### Exact prompt — basalt.jpg

Use case: product-mockup. Asset type: seamless photographic PBR albedo texture for dark carved stone chess pieces. Entire square is a continuous orthographic evenly lit close-up scan of matte charcoal grey basalt. Natural weathered dark grey volcanic stone with visible tiny pores, fine granular crystalline structure, subtle wispy mineral deposits, occasional muted brown and warm grey speckles. Raw dark graphite, smoke and earthy charcoal rather than pure black. Very fine gentle nonuniform surface, small pinholes, slight weathering. No glossy polish, no strong white veins, no tile grid, no objects or text. Seamless tileable texture. Even diffuse lighting no hard shadows or lighting gradient. Photorealistic tactile fine detail at a 20cm material scale. Suitable for applying as color and relief on a carved solid stone sculpture. Not asphalt, no large aggregate, no wood.
