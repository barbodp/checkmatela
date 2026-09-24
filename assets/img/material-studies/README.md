# Checkmatela material studies

- `hero-wood.html`: five independently clickable walnut pieces with faceted profiles.
- `hero-stone.html`: five independently clickable travertine pieces with rounded profiles.
- King → Men, Queen → Women (coming soon), Pawn → Kids, Bishop → Accessories, Rook → Shoes.
- Drag or use canvas arrow keys to turn the view. Plus/minus zoom. Home resets the view.
- Closer look frames a selected piece; the selector covers all five categories.
- The scene renders on demand. There is no idle motion, hover lift, glow, or delayed navigation.
- The JPEG previews are screenshots of the actual WebGL scenes, used when JavaScript or WebGL is unavailable. Category links remain regular HTML links.

## Assets and rendering

Textures generated with the built-in image-generation tool on 2026-09-24. JPEG copies are saved here; the generated originals remain in Codex's generated-images directory. The textures are synthetic photographic material studies, not scans of the user's physical references. Meshes are authored in `js/material-study.js` and rendered by the existing local Three.js 0.159 module. The models are actual interactive geometry, not image planes. World-space texture mapping supplies surface color and bump relief; the finish uses nonmetallic rough materials and soft shadows.

The sample stylesheet is standalone and has its own versioned URL (`material-study.css?v=3`). Shared storefront styles and the homepage are not changed.

## Exact texture prompts

### Walnut

Use case: product-mockup. Asset type: seamless PBR albedo texture for a real-time 3D carved wooden chess set. Create a square 2048px photographic flat material texture, edge to edge, of aged medium brown walnut heartwood, inspired by hand-carved geometric wooden chess pieces. Beautiful very clearly visible narrow vertical wavy long wood grain, small open pores, gently undulating fibers, subtle small natural knots, fine parallel tool traces. Rich desaturated tobacco brown and warm grey brown, natural satin matte unfinished wood. Orthographic flat scan of a wood surface under perfectly even diffuse illumination, no specular highlights, no lighting gradient, no shadows, no 3D objects, no chess pieces, no text, no borders. Seamless repeatable texture. Fine tactile realistic wood fibers visible at close range, natural detailed photographic variation without excessive visual noise. Entire image is one continuous wood surface.

### Travertine

Use case: product-mockup. Asset type: seamless PBR albedo texture for a real-time 3D carved travertine chess set. Create a square 2048px photographic flat material texture of natural ivory cream travertine limestone, entire image is continuous stone surface. Real unfilled porous Italian travertine, irregular little cavities and pinholes, some longer natural crevices, fine fossil grains, softly stratified mineral color. Warm pale cream ivory with pale beige variation, not yellow, not shiny. Cavities should be visibly darker taupe and occur at multiple tiny scales; natural organic porous structure as seen on an expensive hand carved stone chess piece. Macro photographic scan of a 25cm square area, orthographic flat even diffuse lighting for PBR, no directional shadows or gradients, no gloss, no chess pieces or other objects, no text, no borders. Surface is matte honed tactile stone, photoreal detail. Seamless tileable. Restrained natural contrast, pores abundantly visible but not huge dark holes.
