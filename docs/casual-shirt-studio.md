# Casual shirt studio image production

Built-in image generation. No real-person identity references.

## Approved aesthetic
Match the generated suit product photographs: seamless white background, soft diffuse lighting, subtle shadows, centered head-to-upper-thigh framing, charcoal trousers, handsome fictional adult male. No marble, furniture, or props.

## Reference roles
1. Angle-specific generated model photo: fixes the fictional model, pose, camera, studio and crop.
2. Exact supplier product photo for that style and color: fixes garment details and color.

## Shared prompt
Use case: product-mockup. Make ONE premium ecommerce photo for CheckmateLA. Reference 1 locks the fictional ADULT male model, EXACT single camera angle, pose, framing, white seamless background, charcoal trousers and soft even studio lighting. Preserve those exactly. Reference 2 is the only garment source: replace the reference 1 shirt with this exact product, faithfully matching fabric color, texture, plaid repeat scale and alignment, collar, pocket count/shape, buttons or snaps, sleeve length and contrasting inner details. Shirt untucked, natural regular fit. ONE adult man only, one continuous anatomically correct silhouette. No combined viewpoints, second person, split panel, collage, double exposure or additional angle. No marble, furniture, props, text, watermark, packaging pins, tags, hanger, shoulder white lines or invented details. Original fictional handsome man, not a real person. Portrait 2:3, entire head, shirt hem and upper thighs visible. 

## Angle prompts
### front
Front view facing camera straight on, both arms relaxed clear of shirt, shirt front completely visible.

### threequarter
Three-quarter view, turn torso 45 degrees to camera, face turned slightly toward lens, arms relaxed clear of shirt. Show the side seam, collar and front fit.

### back
STRICT SINGLE STRAIGHT-ON BACK VIEW. Camera centered directly behind model at mid torso height, optical axis perpendicular to the model's back. Both shoulders exactly level and square to camera, equal shoulder widths, spine vertical and centered, torso and hips parallel to sensor. Head faces directly away, show only back of head, no face or cheek. Both arms straight relaxed symmetrically, show full back, both sleeves and untucked hem equally. No rotation, twist, three-quarter perspective, double exposure, split view, composite viewpoint or second angle. One continuous anatomically correct rear silhouette. Match the straight-on rear framing of the existing suit galleries. Natural back yoke only, no invented adornments, neck buttons, shoulder pins or white lines.

## Product-specific prompt suffix
Product: {exact product name}. Exact color: {exact option value}. Preserve sleeve length, collar, pocket count/shape, button or snap closure, textile pattern scale, and interior contrast from the supplied garment reference.

## Organization
Each style/color has separate front.webp, threequarter.webp, back.webp and small thumbnail files. The manifest tools/catalog/casual-shirt-studio.json maps them to the supplier color option, independently of automatic stock sync. Show these three model photos first, then only original product images tagged for that selected color. Every rear image must show one adult model in a perfectly straight-on rear view; reject images combining front/back views.
