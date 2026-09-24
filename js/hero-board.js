/* Homepage hero: an interactive 3D chessboard where the pieces are the navigation.

   Hover a piece  → it lifts, glows brass, a label says where it leads ("King — Men").
   Click a piece  → it makes its own chess move (king steps, rook slides, bishop cuts a diagonal, knight hops in an L…),
                    the camera dives to it, the page dissolves, and you land on that section.
   Every piece also exists as a link in the key row under the board (keyboard / touch / no-WebGL fallback).

   Built with three.js (vendored in js/vendor). Pieces are generated procedurally (lathe profiles + a few extras), so there
   are no model files. Tweak: DEST/LABEL (where pieces go), LAYOUT (where they stand), MOVES (how each one moves),
   materials in makeMaterials(), camera in fit().

   Test hooks: window.__hb = { advance(sec), state, noNav } — advance drives the timeline by hand when the browser pane is hidden. */
(() => {
  "use strict";
  const root = document.getElementById('heroBoard');
  if (!root) return;
  const canvas = root.querySelector('.hb-canvas'), tip = root.querySelector('.hb-tip'), wipe = root.querySelector('.hb-wipe');
  const keys = [...root.querySelectorAll('.hb-key')];
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const DEST = { king: 'king.html', queen: 'queen.html', pawn: 'pawn.html', bishop: 'bishop.html', rook: 'rook.html', knight: 'book-a-fitting.html' };
  const LABEL = { king: 'King — Men', queen: 'Queen — Women', pawn: 'Pawn — Kids', bishop: 'Bishop — Accessories', rook: 'Rook — Shoes', knight: 'Knight — Book a fitting' };
  // A standard starting position: white (clickable) on ranks 1-2 nearest the camera, black (scenery) on ranks 7-8.
  const BACK = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'];
  const WHITE = [...BACK.map((t, f) => [t, f, 0]), ...Array.from({ length: 8 }, (_, f) => ['pawn', f, 1])];
  const BLACK = [...BACK.map((t, f) => [t, f, 7]), ...Array.from({ length: 8 }, (_, f) => ['pawn', f, 6])];
  // how each type moves when clicked (from the start position, over the pieces in front): [file delta, rank delta, hop height]
  const MOVES = { pawn: () => [0, 2, .6], rook: () => [0, 3, 1.6], bishop: f => [f < 4 ? 2 : -2, 2, 1.3], queen: () => [3, 3, 1.4], king: () => [0, 2, 1.3], knight: f => [f < 4 ? 1 : -1, 2, 1.5] };
  const PREFER = { king: 4, queen: 3, bishop: 5, rook: 7, knight: 6, pawn: 4 };   // which piece the key row / hover shortcuts refer to
  const SCALE = 1.0;

  let THREE = null, renderer, scene, camera, ring, envTex;
  const mirrors = [];
  let blobMat = null;
  const pieces = [];                                             // all pieces {type,color,group,file,rank,home,mat,...}
  const interactive = [];                                        // white pieces
  let hovered = null, busy = false, T = 0, tweens = [], pointer = { x: 0, y: 0, in: false }, camState = { x: 0, y: 0 };
  let dive = null, idleAt = 4, running = false;

  const sqx = f => f - 3.5, sqz = r => 3.5 - r, TOP = .14;
  const lerp = (a, b, k) => a + (b - a) * k, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const easeIO = k => (k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2), easeOut = k => 1 - Math.pow(1 - k, 3);

  /* ---------------------------------------------------------------- timeline */
  const tween = (dur, fn, ease = easeIO) => new Promise(res => { tweens.push({ t0: T, dur, fn, ease, res }); });
  function runTweens() {
    for (const tw of tweens.slice()) {
      const k = clamp((T - tw.t0) / tw.dur, 0, 1);
      tw.fn(tw.ease(k), k);
      if (k >= 1) { tweens.splice(tweens.indexOf(tw), 1); tw.res(); }
    }
  }

  /* ---------------------------------------------------------------- pieces */
  function makeMaterials() {
    const T3 = THREE, tex = c => { const t = new T3.CanvasTexture(c); t.colorSpace = T3.SRGBColorSpace; t.wrapS = t.wrapT = T3.RepeatWrapping; t.anisotropy = 8; return t; };
    // raw, unfinished wood: matte, no clear coat, the grain drives colour and a very gentle relief. Same grain in both woods.
    const wood = (canvas, ru) => { const t = tex(canvas); t.repeat.set(ru, 1);
      return new T3.MeshStandardMaterial({ map: t, bumpMap: t, bumpScale: .8, roughness: .84, metalness: 0, flatShading: true, envMapIntensity: .55 }); };
    return { ivory: wood(woodGrainCanvas('light'), 2), ebony: wood(woodGrainCanvas('dark'), 2) };
  }
  const geoCache = {};
  function G(key, make) { return geoCache[key] || (geoCache[key] = make()); }
  const lathe = (pts, seg = 40) => new THREE.LatheGeometry(new THREE.SplineCurve(pts.map(p => new THREE.Vector2(p[0], p[1]))).getPoints(40), seg);
  const cyl = (rt, rb, h, seg = 40) => new THREE.CylinderGeometry(rt, rb, h, seg);

  /* Slim, faceted, hand-carved Staunton-inspired pieces (after the user's reference photo): low-segment lathes with flat shading give
     the cut-gem facets; round stone finials (pawn, queen, bishop), a block cross for the king, a faceted horse head for the knight,
     and a few brass rings for restrained flare. Profiles are [radius, height] polylines from the base up. */
  const SEG = 28;
  const facet = (pts, seg = SEG) => new THREE.LatheGeometry(pts.map(p => new THREE.Vector2(p[0], p[1])), seg);
  const FOOT = [[0, 0], [.35, 0], [.37, .045], [.32, .115], [.245, .15]];
  const ringG = (r, t) => new THREE.TorusGeometry(r, t, 8, 40);
  function buildPiece(type, body, trim, ball) {
    const g = new THREE.Group(), add = (geo, mat, x = 0, y = 0, z = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m; };
    const band = (y, r, t = .014) => { const m = add(G('rg' + r + t, () => ringG(r, t)), trim, 0, y); m.rotation.x = Math.PI / 2; m.castShadow = false; return m; };
    const stem = (key, pts) => add(G(key, () => facet(FOOT.concat(pts))), body);
    add(G('felt', () => new THREE.CylinderGeometry(.32, .32, .012, 10)), FELT, 0, .006);
    let h = 1;
    if (type === 'pawn') {
      stem('pawn', [[.29, .25], [.235, .4], [.15, .62], [.115, .78], [.2, .81], [.2, .86], [.12, .89], [.085, .92], [.085, .98]]);
      band(.83, .2); add(G('pawnBall', () => new THREE.SphereGeometry(.2, 40, 30)), ball, 0, 1.14); h = 1.34;
    } else if (type === 'rook') {
      stem('rook', [[.31, .26], [.255, .5], [.215, .84], [.27, .94], [.31, .99], [.31, 1.13], [.245, 1.14]]);
      band(.97, .29);
      add(G('rookIn', () => new THREE.CylinderGeometry(.22, .22, .01, 10)), new THREE.MeshStandardMaterial({ color: 0x1c130c, roughness: .9 }), 0, 1.145);
      for (let i = 0; i < 4; i++) { const a = i / 4 * Math.PI * 2 + Math.PI / 4, m = add(G('mer', () => new THREE.BoxGeometry(.17, .16, .11)), body, Math.sin(a) * .245, 1.2, Math.cos(a) * .245); m.rotation.y = a; }
      h = 1.3;
    } else if (type === 'bishop') {
      stem('bishopB', [[.3, .24], [.22, .42], [.15, .7], [.12, .9], [.205, .93], [.205, .98], [.12, 1.0]]);
      add(G('bishopH', () => facet([[.12, 1.0], [.2, 1.07], [.245, 1.22], [.19, 1.42], [.085, 1.57], [0, 1.63]], 8)), body);
      band(.955, .205);
      const notch = add(G('notch', () => new THREE.BoxGeometry(.4, .028, .05)), SLIT, 0, 1.3, 0); notch.rotation.z = -.7; notch.castShadow = false;
      add(G('bishopBall', () => new THREE.SphereGeometry(.055, 24, 18)), ball, 0, 1.67); h = 1.75;
    } else if (type === 'queen') {
      stem('queenB', [[.32, .26], [.245, .5], [.165, .85], [.13, 1.08], [.265, 1.11], [.265, 1.17], [.14, 1.2]]);
      add(G('queenH', () => facet([[.14, 1.2], [.31, 1.43], [.215, 1.65], [.06, 1.79], [0, 1.82]], 8)), body);
      band(1.14, .265);
      add(G('queenBall', () => new THREE.SphereGeometry(.07, 28, 20)), ball, 0, 1.89); h = 1.97;
    } else if (type === 'king') {
      stem('kingB', [[.32, .26], [.245, .5], [.165, .85], [.13, 1.08], [.265, 1.11], [.265, 1.17], [.14, 1.2]]);
      add(G('kingH', () => facet([[.14, 1.2], [.27, 1.38], [.3, 1.56], [.17, 1.74], [.12, 1.8], [.12, 1.85]], 8)), body);
      band(1.14, .265);
      add(G('kingBlock', () => new THREE.BoxGeometry(.17, .09, .17)), trim, 0, 1.9); add(G('kv', () => new THREE.BoxGeometry(.08, .3, .08)), body, 0, 2.07); add(G('kh', () => new THREE.BoxGeometry(.25, .08, .08)), body, 0, 2.1); h = 2.24;
    } else if (type === 'knight') {
      stem('knightB', [[.3, .26], [.235, .44], [.2, .66], [.245, .71]]);
      band(.72, .245);
      const geo = G('knightH', () => {
        const pts = [[-.2, .72], [-.27, .96], [-.23, 1.24], [-.09, 1.44], [.05, 1.5], [.13, 1.36], [.45, 1.15], [.53, 1.03], [.48, .91], [.37, .87], [.25, .95], [.14, .91], [.21, .81], [.3, .73]];
        const shape = new THREE.Shape(pts.map(p => new THREE.Vector2(p[0], p[1])));
        const e = new THREE.ExtrudeGeometry(shape, { depth: .26, bevelEnabled: true, bevelSize: .06, bevelThickness: .07, bevelSegments: 3, curveSegments: 1, steps: 1 });
        e.translate(0, 0, -.13); return e;
      });
      const m = add(geo, body); m.rotation.y = Math.PI / 2;
      [-1, 1].forEach(sd => { const ear = add(G('ear', () => new THREE.ConeGeometry(.07, .24, 4)), body, sd * .11, 1.6, -.02); ear.rotation.z = -sd * .12; ear.rotation.x = -.15; });
      [-1, 1].forEach(sd => { const e = add(G('eye', () => new THREE.SphereGeometry(.026, 12, 10)), SLIT, sd * .185, 1.24, -.13); e.castShadow = false; });
      h = 1.62;
    }
    g.userData.h = h;
    return g;
  }
  let FELT, SLIT, INK;

  function addPiece(type, file, rank, white, M) {
    const bodyMat = M[white ? 'ivory' : 'ebony'].clone();
    const g = buildPiece(type, bodyMat, bodyMat, bodyMat);
    g.scale.setScalar(SCALE);
    g.position.set(sqx(file), TOP, sqz(rank));
    if (!white) g.rotation.y = Math.PI;
    if (type === 'knight') g.rotation.y += (white ? 1 : -1) * (file > 3 ? -.75 : .75);
    scene.add(g);
    addMirror(g);                                   // clone before userData.piece is set (clone() serialises userData)
    const blob = new THREE.Mesh(new THREE.PlaneGeometry(1.55, 1.55), blobMat); blob.rotation.x = -Math.PI / 2; blob.position.set(g.position.x, TOP + .003, g.position.z); blob.renderOrder = 3; scene.add(blob);
    const p = { blob, type, white, group: g, file, rank, mat: bodyMat, home: g.position.clone(), homeRot: g.rotation.y, lift: 0, glow: 0, h: g.userData.h * SCALE };
    g.traverse(o => { if (o.isMesh) o.userData.piece = p; });
    pieces.push(p); if (white) interactive.push(p);
    return p;
  }

  /* Glossy-floor reflection: a darker, upside-down twin of every piece under the (slightly see-through) board. */
  const reflectM = () => new THREE.Matrix4().makeTranslation(0, 2 * TOP, 0).multiply(new THREE.Matrix4().makeScale(1, -1, 1));
  function addMirror(src) {
    const m = src.clone(true);
    m.traverse(o => { if (o.isMesh) { o.castShadow = o.receiveShadow = false; o.material = o.material.clone(); o.material.transparent = true; o.material.opacity = .5; o.material.depthWrite = false; o.renderOrder = 1; if (o.material.color) o.material.color.multiplyScalar(.9); if (o.material.emissive) o.material.emissive.setHex(0); } });
    m.matrixAutoUpdate = false; scene.add(m); mirrors.push([src, m]);
  }
  function syncMirrors() { const R = reflectM(); for (const [src, m] of mirrors) { src.updateMatrixWorld(true); m.matrix.copy(R).multiply(src.matrixWorld); m.matrixWorldNeedsUpdate = true; } }

  /* ---------------------------------------------------------------- scene */
  function makeEnv() {
    const s = new THREE.Scene();
    s.add(new THREE.Mesh(new THREE.BoxGeometry(50, 50, 50), new THREE.MeshBasicMaterial({ color: 0x0a0b0c, side: THREE.BackSide })));
    const panel = (w, h, pos, rot, c) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(c, c, c), side: THREE.DoubleSide })); m.position.set(...pos); m.rotation.set(...rot); s.add(m); };
    panel(30, 8, [0, 16, -2], [Math.PI / 2, 0, 0], 16);                       // overhead softbox
    panel(2.6, 20, [-13, 6, 6], [0, Math.PI / 2.2, 0], 20); panel(2.6, 20, [-6, 6, 14], [0, Math.PI / 1.5, 0], 14);   // tall strips, left / front-left
    panel(2.6, 20, [13, 6, 4], [0, -Math.PI / 2.2, 0], 12);                    // strip, right
    panel(12, 3, [0, 3, -16], [0, 0, 0], 5);                                  // back wall glow
    return s;
  }

  /* ---------------------------------------------------------------- procedural textures */
  const hash = (x, y) => { const n = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return n - Math.floor(n); };
  const vnoise = (x, y) => { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    return lerp(lerp(hash(xi, yi), hash(xi + 1, yi), u), lerp(hash(xi, yi + 1), hash(xi + 1, yi + 1), u), v); };
  const fbm = (x, y, o = 5) => { let a = .5, f = 1, t = 0; for (let i = 0; i < o; i++) { t += a * vnoise(x * f, y * f); f *= 2; a *= .5; } return t; };
  function marbleCanvas(kind) {
    const N = 384, c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'), img = g.createImageData(N, N), d = img.data;
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const u = x / N, v = y / N, n = fbm(u * 3.2, v * 3.2), w = fbm(u * 6 + 7, v * 6 + 3, 4);
      const t = Math.abs(Math.sin((u * 5.0 + v * 2.4 + n * 3.4) * Math.PI)), vein = Math.pow(1 - t, 14), vein2 = Math.pow(1 - Math.abs(Math.sin((v * 7 - u * 3 + w * 2.6) * Math.PI)), 20);
      let r, gg, b;
      if (kind === 'light') { const base = 214 + n * 26 - 14; r = base - vein * 74 - vein2 * 30; gg = base - 2 - vein * 72 - vein2 * 30; b = base - 8 - vein * 62 - vein2 * 26; }
      else { const base = 9 + n * 12; r = base + vein * 46 + vein2 * 14; gg = base + vein * 43 + vein2 * 12; b = base + 1 + vein * 38 + vein2 * 10; }
      const i = (y * N + x) * 4; d[i] = clamp(r, 0, 255); d[i + 1] = clamp(gg, 0, 255); d[i + 2] = clamp(b, 0, 255); d[i + 3] = 255;
    }
    g.putImageData(img, 0, 0); return c;
  }
  function woodGrainCanvas(kind) {
    const N = 512, c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'), img = g.createImageData(N, N), d = img.data;
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const u = x / N, v = y / N;
      // growth rings: wandering, uneven bands (low-frequency warp) + fine pores and fibres, identical for both woods
      const w = fbm(u * 2.0 + 4, v * .5, 4) * 6, ring = .5 + .5 * Math.sin((u * 8 + w) * Math.PI * 2), soft = ring * ring * (3 - 2 * ring);
      const pore = vnoise(u * 190, v * 5), fibre = fbm(u * 70, v * 2.5, 3), tone = fbm(u * 1.3, v * .4, 4);
      const heart = .5 + .5 * Math.sin((u * 3.2 + tone * 2.4) * Math.PI);                        // broad colour drift (heartwood / sapwood)
      let r, gg, b;
      if (kind === 'dark') {                                                                     // walnut
        const late = 1 - soft, k = .9 + tone * .35 + (fibre - .5) * .28 + (pore > .86 ? -.16 : 0);
        r = (84 - 44 * late + 16 * heart) * k; gg = (56 - 30 * late + 11 * heart) * k; b = (38 - 21 * late + 7 * heart) * k;
      } else {                                                                                   // pale oak / ash
        const late = 1 - soft, k = .92 + tone * .3 + (fibre - .5) * .22 + (pore > .86 ? -.1 : 0);
        r = (212 - 70 * late - 10 * heart) * k; gg = (178 - 68 * late - 12 * heart) * k; b = (130 - 58 * late - 10 * heart) * k;
      }
      const i = (y * N + x) * 4; d[i] = clamp(r, 0, 255); d[i + 1] = clamp(gg, 0, 255); d[i + 2] = clamp(b, 0, 255); d[i + 3] = 255;
    }
    g.putImageData(img, 0, 0); return c;
  }
  function woodCanvas() {
    const W = 512, H = 128, c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d'), img = g.createImageData(W, H), d = img.data;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const grain = fbm(x * .012, y * .18, 5), ring = .5 + .5 * Math.sin((y * .11 + grain * 9) * 1.0), k = .42 + grain * .5 + ring * .18;
      const i = (y * W + x) * 4; d[i] = clamp(62 * k + 12, 0, 255); d[i + 1] = clamp(38 * k + 8, 0, 255); d[i + 2] = clamp(24 * k + 5, 0, 255); d[i + 3] = 255;
    }
    g.putImageData(img, 0, 0); return c;
  }

  async function boot() {
    THREE = await import('./vendor/three-0.159.module.min.js');
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = .98;
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; renderer.setClearColor(0, 0);
    scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x060708, 20, 40);                     // distant squares fade into the dark, like the reference
    camera = new THREE.PerspectiveCamera(28, 1, .1, 100);
    const pm = new THREE.PMREMGenerator(renderer); envTex = pm.fromScene(makeEnv(), .02).texture; scene.environment = envTex;
    const sun = new THREE.DirectionalLight(0xffffff, 1.5); sun.position.set(-6, 9, 7); sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8, near: 1, far: 30 }); sun.shadow.bias = -.0004; sun.shadow.radius = 5;
    scene.add(sun);

    FELT = new THREE.MeshStandardMaterial({ color: 0x0c0c0c, roughness: .95 }); SLIT = new THREE.MeshStandardMaterial({ color: 0x24170e, roughness: .95 }); INK = new THREE.MeshBasicMaterial({ color: 0x111111 });

    // ---- the board: polished marble squares (white Carrara-style / black with faint veins) in a dark walnut frame with a brass inlay.
    // The squares are slightly see-through so the upside-down twins of the pieces read as reflections in the polish.
    const marble = kind => { const t = new THREE.CanvasTexture(marbleCanvas(kind)); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4; return t; };
    const texL = marble('light'), texD = marble('dark');
    const variants = (tex, base, opacity) => Array.from({ length: 6 }, (_, i) => { const t = tex.clone(); t.needsUpdate = true; t.repeat.set(.5, .5); t.offset.set((i % 3) * .25 + .0, Math.floor(i / 3) * .5); t.center.set(.5, .5); t.rotation = (i % 4) * Math.PI / 2;
      return new THREE.MeshPhysicalMaterial({ map: t, color: base, roughness: .06, clearcoat: 1, clearcoatRoughness: .02, transparent: true, opacity, envMapIntensity: 1.4 }); });
    const lights = variants(texL, 0xffffff, .94), darks = variants(texD, 0xffffff, .72);
    const sqGeo = new THREE.BoxGeometry(.995, .06, .995);
    for (let f = 0; f < 8; f++) for (let r = 0; r < 8; r++) {
      const set = (f + r) % 2 ? lights : darks, m = new THREE.Mesh(sqGeo, set[(f * 7 + r * 3) % set.length]);
      m.position.set(sqx(f), TOP - .03, sqz(r)); m.receiveShadow = true; m.renderOrder = 2; scene.add(m);
    }
    const wood = new THREE.CanvasTexture(woodCanvas()); wood.colorSpace = THREE.SRGBColorSpace; wood.wrapS = wood.wrapT = THREE.RepeatWrapping;
    const woodM = new THREE.MeshPhysicalMaterial({ map: wood, color: 0x8f7a6a, roughness: .3, clearcoat: .9, clearcoatRoughness: .08, envMapIntensity: 1.1 });
    const brass = new THREE.MeshStandardMaterial({ color: 0xd8aa52, metalness: 1, roughness: .2 });
    const W = 8, B = .55, H = .24;
    // dark skirt under the frame: hides the reflection twins from the sides so they only show through the marble
    { const wallM = new THREE.MeshBasicMaterial({ color: 0x070809, side: THREE.DoubleSide }), hh = 3.4, yy = TOP - hh / 2 - .05, o = W / 2 + B - .02;
      [[0, -o, W + B * 2, .02], [0, o, W + B * 2, .02], [-o, 0, .02, W + B * 2], [o, 0, .02, W + B * 2]].forEach(([x, z, w, d]) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, hh, d), wallM); m.position.set(x, yy, z); scene.add(m); }); }
    [[0, -(W / 2 + B / 2), W + B * 2, B], [0, W / 2 + B / 2, W + B * 2, B], [-(W / 2 + B / 2), 0, B, W], [W / 2 + B / 2, 0, B, W]].forEach(([x, z, w, d]) => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, H, d), woodM); m.position.set(x, TOP + .02 - H / 2 + .03, z); m.castShadow = m.receiveShadow = true; scene.add(m);
    });
    [[0, -W / 2 - .02, W + .06, .03], [0, W / 2 + .02, W + .06, .03], [-W / 2 - .02, 0, .03, W], [W / 2 + .02, 0, .03, W]].forEach(([x, z, w, d]) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, .02, d), brass); m.position.set(x, TOP + .056, z); scene.add(m); });
    ring = new THREE.Mesh(new THREE.RingGeometry(.5, .62, 56), new THREE.MeshBasicMaterial({ color: 0xd8aa52, transparent: true, opacity: 0, side: THREE.DoubleSide, fog: false })); ring.rotation.x = -Math.PI / 2; ring.position.y = TOP + .004; ring.renderOrder = 3; scene.add(ring);

    // soft contact shadow under every piece (grounds them, like ambient occlusion)
    const bc = document.createElement('canvas'); bc.width = bc.height = 128; const bg = bc.getContext('2d'), gr = bg.createRadialGradient(64, 64, 6, 64, 64, 62); gr.addColorStop(0, 'rgba(0,0,0,.75)'); gr.addColorStop(.55, 'rgba(0,0,0,.32)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); bg.fillStyle = gr; bg.fillRect(0, 0, 128, 128);
    blobMat = new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(bc), transparent: true, depthWrite: false, opacity: .8, fog: false });

    const M = makeMaterials();
    WHITE.forEach(([t, f, r]) => addPiece(t, f, r, true, M)); BLACK.forEach(([t, f, r]) => addPiece(t, f, r, false, M));
    fit(); new ResizeObserver(fit).observe(root);
    bindEvents();
    root.classList.add('is-ready');
    running = true; requestAnimationFrame(loop);
  }

  function fit() {
    if (!renderer) return;
    const w = root.clientWidth, h = root.clientHeight;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2)); renderer.setSize(w, h, false);
    camera.aspect = w / h;
    const wide = w > 900, usable = wide ? .66 : .98;
    const t = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    camState.dist = 5.4 / (t * camera.aspect * usable);
    scene.fog.near = camState.dist * .95; scene.fog.far = camState.dist * 2.15;
    camera.setViewOffset(w, h, wide ? -w * .15 : 0, wide ? h * .03 : -h * .1, w, h);
    camera.updateProjectionMatrix();
  }

  /* ---------------------------------------------------------------- interaction */
  const ray = () => new THREE.Raycaster();
  let raycaster = null;
  function pick(clientX, clientY) {
    const r = canvas.getBoundingClientRect();
    pointer.x = ((clientX - r.left) / r.width) * 2 - 1; pointer.y = -(((clientY - r.top) / r.height) * 2 - 1);
    raycaster = raycaster || ray(); raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(interactive.map(p => p.group), true)[0];
    return hit ? hit.object.userData.piece : null;
  }
  const prefetched = new Set();
  function prefetch(url) { if (prefetched.has(url)) return; prefetched.add(url); const l = document.createElement('link'); l.rel = 'prefetch'; l.href = url; document.head.appendChild(l); }
  function setHover(p) {
    if (busy || p === hovered) return;
    hovered = p;
    keys.forEach(k => k.classList.toggle('is-on', !!p && k.dataset.piece === p.type));
    canvas.style.cursor = p ? 'pointer' : '';
    if (p) { prefetch(DEST[p.type]); tip.textContent = LABEL[p.type]; tip.classList.add('is-on'); } else tip.classList.remove('is-on');
  }
  const home = type => interactive.find(p => p.type === type && p.file === PREFER[type] && (type !== 'pawn' || p.rank === 1)) || interactive.find(p => p.type === type);

  function bindEvents() {
    canvas.addEventListener('pointermove', e => { pointer.in = true; if (e.pointerType === 'touch') return; setHover(pick(e.clientX, e.clientY)); });
    canvas.addEventListener('pointerleave', () => { pointer.in = false; setHover(null); });
    canvas.addEventListener('click', e => { const p = pick(e.clientX, e.clientY); if (p) choose(p); });
    keys.forEach(k => {
      const t = k.dataset.piece;
      k.addEventListener('mouseenter', () => setHover(home(t))); k.addEventListener('focus', () => setHover(home(t)));
      k.addEventListener('mouseleave', () => setHover(null)); k.addEventListener('blur', () => setHover(null));
      k.addEventListener('click', e => { if (e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); choose(home(t)); });
    });
    window.addEventListener('pageshow', e => { if (e.persisted) resetAfterBack(); });
  }

  /* ---------------------------------------------------------------- the click sequence */
  const go = url => { if (window.__hb && window.__hb.noNav) { window.__hb.lastNav = url; return; } window.location.href = url; };
  async function choose(p) {
    if (!p || busy) return;
    busy = true; setHover(p); const url = DEST[p.type];
    if (reduce) { go(url); return; }
    tip.textContent = LABEL[p.type]; tip.classList.add('is-on'); root.classList.add('is-moving');
    const g = p.group, x0 = p.home.x, z0 = p.home.z;
    const [df, dr, hop] = MOVES[p.type](p.file);
    const x1 = sqx(p.file + df), z1 = sqz(p.rank + dr);
    ring.material.opacity = 0;
    // 1) lift & spin, 2) glide along the move with an arc, 3) settle
    await tween(.4, k => { g.position.y = TOP + hop * .55 * k; g.rotation.y = p.homeRot + k * Math.PI; }, easeOut);
    await tween(.85, k => { g.position.x = lerp(x0, x1, k); g.position.z = lerp(z0, z1, k); g.position.y = TOP + hop * (.55 + .45 * Math.sin(Math.PI * k)) * (1 - .45 * k); g.rotation.y = p.homeRot + Math.PI + k * Math.PI; });
    await tween(.22, k => { g.position.y = lerp(TOP + hop * .25, TOP, k); }, easeOut);
    // 4) camera dives to the piece while the page dissolves
    dive = { from: camState.snap(), to: new THREE.Vector3(x1 + .2, TOP + p.h * .95, z1 + 2.6), look: new THREE.Vector3(x1, TOP + p.h * .72, z1), fov: 15 };
    root.classList.add('is-diving');
    await tween(1.0, k => { dive.k = k; wipe.style.opacity = clamp((k - .62) / .38, 0, 1).toFixed(3); });
    go(url);
  }
  function resetAfterBack() {
    busy = false; dive = null; wipe.style.opacity = 0; root.classList.remove('is-moving', 'is-diving'); tweens = [];
    pieces.forEach(p => { p.group.position.copy(p.home); p.group.rotation.y = p.homeRot; }); setHover(null);
  }

  /* ---------------------------------------------------------------- frame loop */
  function placeCamera(dt) {
    const el = THREE.MathUtils.degToRad(29), d = camState.dist;
    camState.x += ((pointer.in ? pointer.x : 0) - camState.x) * Math.min(1, dt * 2.2); camState.y += ((pointer.in ? pointer.y : 0) - camState.y) * Math.min(1, dt * 2.2);
    const yaw = camState.x * .09 + Math.sin(T * .18) * .035, elv = el + camState.y * .03;
    const target = new THREE.Vector3(0, .8, .6), pos = new THREE.Vector3(Math.sin(yaw) * Math.cos(elv) * d, Math.sin(elv) * d + .8, Math.cos(yaw) * Math.cos(elv) * d + .6);
    if (dive) {
      const k = easeIO(dive.k || 0);
      camera.position.lerpVectors(pos, dive.to, k); target.lerp(dive.look, k); camera.fov = lerp(28, dive.fov, k); camera.updateProjectionMatrix();
    } else camera.position.copy(pos);
    camera.lookAt(target);
  }
  camState.snap = () => camera.position.clone();

  function update(dt) {
    T += dt; runTweens();
    for (const p of interactive) {
      const on = p === hovered && !busy;
      p.lift += ((on ? .26 : 0) - p.lift) * Math.min(1, dt * 9); p.glow += ((on ? .38 : 0) - p.glow) * Math.min(1, dt * 9);
      if (!busy) p.group.position.y = TOP + p.lift + (p.nudge ? Math.sin(clamp((T - p.nudge) / .7, 0, 1) * Math.PI) * .16 : 0);
      p.mat.emissive.setHex(0xb8862e); p.mat.emissiveIntensity = p.glow;
    }
    // hover ring on the square + label following the piece
    if (hovered && !busy) { ring.position.set(hovered.home.x, TOP + .004, hovered.home.z); ring.material.opacity += (.95 - ring.material.opacity) * Math.min(1, dt * 10); }
    else ring.material.opacity += (0 - ring.material.opacity) * Math.min(1, dt * 10);
    // idle: every few seconds one piece nudges to say "I'm clickable"
    if (!busy && !hovered && T > idleAt) { const p = interactive[Math.floor(Math.random() * interactive.length)]; p.nudge = T; idleAt = T + 3.5 + Math.random() * 3; }
    placeCamera(dt);
    if (tip.classList.contains('is-on')) {
      const p = hovered || interactive.find(q => q.group.position.y > TOP + .3);
      if (p) { const v = p.group.position.clone(); v.y += p.h + .35; v.project(camera); const r = canvas.getBoundingClientRect(); tip.style.transform = `translate(${((v.x + 1) / 2) * r.width}px, ${((1 - v.y) / 2) * r.height}px) translate(-50%, -100%)`; }
    }
    for (const p of pieces) { const y = p.group.position.y - TOP; p.blob.position.x = p.group.position.x; p.blob.position.z = p.group.position.z; p.blob.scale.setScalar(1 + y * .5); }
    syncMirrors();
    renderer.render(scene, camera);
  }
  let last = 0;
  function loop(now) { requestAnimationFrame(loop); if (document.hidden) return; const dt = Math.min(.05, (now - last) / 1000 || .016); last = now; update(dt); }

  /* ---------------------------------------------------------------- start */
  const webgl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; } })();
  window.__hb = { advance(sec) { for (let i = 0; i < Math.round(sec / .02); i++) update(.02); }, get state() { return { busy, hovered: hovered && hovered.type, pieces: pieces.length }; }, noNav: false, zoom(t, k = .9, fov = 17) { const p = home(t); dive = { to: new THREE.Vector3(p.home.x + .3, TOP + p.h * .8, p.home.z + 3.6), look: new THREE.Vector3(p.home.x, TOP + p.h * .62, p.home.z), fov, k }; }, unzoom() { dive = null; }, hover(t) { setHover(home(t)); }, click(t) { return choose(home(t)); } };
  keys.forEach(k => k.addEventListener('click', e => { if (!root.classList.contains('is-ready')) return; }));
  if (!webgl || reduce) { root.classList.add('is-fallback'); return; }
  boot().catch(err => { console.error('hero-board:', err); root.classList.add('is-fallback'); });
})();
