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
    const T3 = THREE, tex = (c, rx = 1, ry = 1) => { const t = new T3.CanvasTexture(c); t.colorSpace = T3.SRGBColorSpace; t.wrapS = t.wrapT = T3.RepeatWrapping; t.anisotropy = 8; t.repeat.set(rx, ry); return t; };
    // white = honed travertine: cream, porous, pitted, satin-matte. black = polished black stone: deep, glossy, faintly mottled.
    const tt = tex(travertineCanvas(), 1.4, 1), bt = tex(blackStoneCanvas(), 1, 1);
    const ivory = new T3.MeshStandardMaterial({ map: tt, bumpMap: tt, color: 0xd8cdb6, bumpScale: 4.2, roughness: .62, metalness: 0, envMapIntensity: .65 });
    const ebony = new T3.MeshPhysicalMaterial({ map: bt, color: 0xffffff, roughness: .07, clearcoat: 1, clearcoatRoughness: .03, envMapIntensity: 1.7 });
    return { ivory, ebony, travertine: tt, blackStone: bt };
  }
  const geoCache = {};
  function G(key, make) { return geoCache[key] || (geoCache[key] = make()); }
  const lathe = (pts, seg = 40) => new THREE.LatheGeometry(new THREE.SplineCurve(pts.map(p => new THREE.Vector2(p[0], p[1]))).getPoints(40), seg);
  const cyl = (rt, rb, h, seg = 40) => new THREE.CylinderGeometry(rt, rb, h, seg);

  /* Turned stone pieces after the user's reference photo: stout-but-elegant Staunton forms with a ribbed, stepped foot,
     incised rings, a ball-headed pawn, crenellated rook, crowned queen/king, mitred bishop and a carved knight. Every part is
     a smooth lathe (profiles are [radius, height] control points) so there are no flat primitives; the surface character comes
     from the travertine / black-stone textures. */
  const spline = (pts, n = 56) => new THREE.SplineCurve(pts.map(p => new THREE.Vector2(p[0], p[1]))).getPoints(n);
  const turn = (pts, seg = 56) => new THREE.LatheGeometry(pts.map(p => new THREE.Vector2(p[0], p[1])), seg);
  const smoothTurn = (pts, seg = 56, n = 56) => new THREE.LatheGeometry(spline(pts, n), seg);
  const footPts = () => { const pts = [[0, 0], [.4, 0], [.425, .022]]; for (let i = 0; i <= 56; i++) { const t = i / 56, y = .035 + .215 * t; pts.push([.425 + (.285 - .425) * t + .022 * Math.pow(Math.max(0, Math.sin(t * 5 * Math.PI)), .55) - .01 * t, y]); } return pts; };   // stepped, ribbed foot
  const beadG = (r, t) => new THREE.TorusGeometry(r, t, 12, 56);
  function buildPiece(type, body, trim, ball) {
    const g = new THREE.Group(), add = (geo, mat, x = 0, y = 0, z = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m; };
    const ring = (y, r, t = .016) => { const m = add(G('bd' + r + t, () => beadG(r, t)), body, 0, y); m.rotation.x = Math.PI / 2; m.castShadow = false; return m; };   // incised/raised ring
    const plate = (y, r, h = .05) => { add(G('pl' + r + h, () => new THREE.CylinderGeometry(r, r * 1.03, h, 56)), body, 0, y); ring(y + h / 2, r * .985, h * .45); ring(y - h / 2, r * 1.0, h * .4); };
    add(G('felt', () => new THREE.CylinderGeometry(.33, .33, .012, 40)), FELT, 0, .006);
    add(G('foot', () => turn(footPts())), body);
    let h = 1;
    if (type === 'pawn') {
      add(G('pawnB', () => smoothTurn([[.285, .25], [.245, .34], [.185, .54], [.15, .74], [.135, .84]])), body);
      ring(.5, .205, .02); ring(.63, .17, .017);
      plate(.86, .235); add(G('pawnN', () => new THREE.CylinderGeometry(.1, .12, .07, 40)), body, 0, .935);
      add(G('pawnBall', () => new THREE.SphereGeometry(.225, 56, 40)), ball, 0, 1.1); h = 1.33;
    } else if (type === 'rook') {
      add(G('rookB', () => smoothTurn([[.285, .25], [.27, .36], [.25, .62], [.235, .86]])), body);
      ring(.5, .262, .02); ring(.6, .255, .017);
      add(G('rookTop', () => smoothTurn([[.235, .86], [.29, .93], [.315, 1.02], [.315, 1.16]])), body);
      add(G('rookCap', () => new THREE.CylinderGeometry(.315, .315, .012, 56)), body, 0, 1.16);
      add(G('rookIn', () => new THREE.CylinderGeometry(.22, .22, .01, 40)), new THREE.MeshStandardMaterial({ color: 0x6f5e46, roughness: .9 }), 0, 1.166);
      for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2, m = add(G('mer', () => new THREE.BoxGeometry(.15, .16, .12)), body, Math.sin(a) * .265, 1.24, Math.cos(a) * .265); m.rotation.y = a; m.scale.set(1, 1, 1); }
      h = 1.34;
    } else if (type === 'bishop') {
      add(G('bishopB', () => smoothTurn([[.285, .25], [.235, .38], [.17, .62], [.13, .86], [.115, .98]])), body);
      ring(.5, .205, .018); plate(1.0, .205, .045);
      add(G('bishopH', () => smoothTurn([[.115, 1.02], [.2, 1.08], [.235, 1.24], [.2, 1.42], [.11, 1.56], [.03, 1.62]], 56, 60)), body);
      add(G('bishopTip', () => new THREE.SphereGeometry(.058, 32, 24)), ball, 0, 1.66);
      const cut = add(G('cut', () => new THREE.BoxGeometry(.4, .028, .06)), SLIT, 0, 1.3, 0); cut.rotation.z = -.7; cut.castShadow = false; h = 1.74;
    } else if (type === 'queen') {
      add(G('queenB', () => smoothTurn([[.285, .25], [.255, .38], [.19, .72], [.145, 1.0], [.125, 1.1]])), body);
      ring(.52, .215, .02); ring(.66, .185, .017); plate(1.13, .27, .05);
      add(G('queenH', () => smoothTurn([[.125, 1.11], [.2, 1.2], [.28, 1.37], [.3, 1.5], [.26, 1.57]], 56, 60)), body);
      for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2; add(G('qb', () => new THREE.SphereGeometry(.042, 20, 16)), body, Math.sin(a) * .265, 1.585, Math.cos(a) * .265); }
      add(G('queenTop', () => new THREE.SphereGeometry(.09, 32, 24)), ball, 0, 1.67); h = 1.78;
    } else if (type === 'king') {
      add(G('kingB', () => smoothTurn([[.285, .25], [.255, .38], [.19, .72], [.145, 1.0], [.125, 1.1]])), body);
      ring(.52, .215, .02); ring(.66, .185, .017); plate(1.13, .27, .05);
      add(G('kingH', () => smoothTurn([[.125, 1.11], [.2, 1.2], [.275, 1.36], [.295, 1.52], [.25, 1.62]], 56, 60)), body);
      add(G('kingDisc', () => new THREE.CylinderGeometry(.215, .235, .05, 56)), body, 0, 1.64);
      add(G('kingCross', () => { const sh = new THREE.Shape([[-.045, 0], [.045, 0], [.045, .17], [.14, .17], [.14, .25], [.045, .25], [.045, .36], [-.045, .36], [-.045, .25], [-.14, .25], [-.14, .17], [-.045, .17]].map(p => new THREE.Vector2(p[0], p[1])));
        const e = new THREE.ExtrudeGeometry(sh, { depth: .09, bevelEnabled: true, bevelSize: .014, bevelThickness: .014, bevelSegments: 3, curveSegments: 1 }); e.translate(0, 0, -.045); return e; }), body, 0, 1.665);
      h = 2.05;
    } else if (type === 'knight') {
      add(G('knightB', () => smoothTurn([[.285, .25], [.245, .4], [.205, .6], [.235, .7]])), body);
      ring(.5, .225, .018); plate(.72, .25, .05);
      const geo = G('knightH', () => {
        const pts = [[-.2, .75], [-.27, .98], [-.23, 1.26], [-.1, 1.46], [.04, 1.52], [.12, 1.38], [.44, 1.17], [.53, 1.05], [.48, .93], [.37, .89], [.25, .97], [.14, .93], [.21, .83], [.3, .76]];
        const shape = new THREE.Shape(new THREE.SplineCurve(pts.concat([pts[0]]).map(p => new THREE.Vector2(p[0], p[1]))).getPoints(120));
        const e = new THREE.ExtrudeGeometry(shape, { depth: .26, bevelEnabled: true, bevelSize: .075, bevelThickness: .08, bevelSegments: 6, curveSegments: 20 });
        e.translate(0, 0, -.13); return e;
      });
      const m = add(geo, body); m.rotation.y = Math.PI / 2;
      [-1, 1].forEach(sd => { const ear = add(G('ear', () => new THREE.ConeGeometry(.065, .23, 20)), body, sd * .1, 1.63, -.03); ear.rotation.z = -sd * .1; ear.rotation.x = -.16; });
      [-1, 1].forEach(sd => { const e = add(G('eye', () => new THREE.SphereGeometry(.026, 12, 10)), SLIT, sd * .19, 1.26, -.13); e.castShadow = false; });
      h = 1.66;
    }
    g.userData.h = h;
    return g;
  }
  let FELT, SLIT, INK;

  function addPiece(type, file, rank, white, M) {
    const bodyMat = M[white ? 'ivory' : 'ebony'].clone();
    // every piece gets its own slice of the stone, so no two pawns share the same pits
    const t1 = M[white ? 'travertine' : 'blackStone'].clone(); t1.offset.set(Math.random(), Math.random()); t1.rotation = Math.random() * .6; t1.needsUpdate = true; bodyMat.map = t1; if (white) bodyMat.bumpMap = t1;
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
  const rngOf = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  function travertineCanvas() {
    const N = 512, c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'), img = g.createImageData(N, N), d = img.data;
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const u = x / N, v = y / N, tone = fbm(u * 2.4, v * 2.4, 4), strata = fbm(u * 2.5, v * 30, 4), grain = fbm(u * 110, v * 110, 2);
      const k = .9 + tone * .22 + (strata - .5) * .2 + (grain - .5) * .07;
      const i = (y * N + x) * 4; d[i] = clamp(226 * k, 0, 255); d[i + 1] = clamp(211 * k, 0, 255); d[i + 2] = clamp(182 * k - strata * 6, 0, 255); d[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    const rnd = rngOf(11);
    // thin bedding lines (travertine is laid down in strata)
    for (let i = 0; i < 14; i++) { const y = rnd() * N, len = 80 + rnd() * 300, x = rnd() * N; g.strokeStyle = `rgba(150,128,96,${.05 + rnd() * .1})`; g.lineWidth = .6 + rnd() * 1.4; g.beginPath(); g.moveTo(x, y); g.lineTo(x + len, y + (rnd() - .5) * 5); g.stroke(); }
    // the pits and voids: elongated along the bedding, dark inside, lit rim on the upper edge
    const pit = (cx, cy, rx, ry) => {
      g.save(); g.translate(cx, cy); g.rotate((rnd() - .5) * .35);
      const gr = g.createRadialGradient(-rx * .12, -ry * .18, 0, 0, 0, Math.max(rx, ry) * 1.15); gr.addColorStop(0, 'rgba(134,112,84,.92)'); gr.addColorStop(.55, 'rgba(166,144,112,.8)'); gr.addColorStop(1, 'rgba(190,170,138,0)');
      g.scale(1, ry / rx); g.beginPath(); g.arc(0, 0, rx, 0, Math.PI * 2); g.fillStyle = gr; g.fill();
      g.beginPath(); g.arc(0, 0, rx * 1.02, Math.PI * 1.05, Math.PI * 1.95); g.strokeStyle = 'rgba(248,238,216,.55)'; g.lineWidth = Math.max(.7, rx * .16); g.stroke(); g.restore();
    };
    for (let i = 0; i < 520; i++) { const big = rnd() < .06, rx = big ? 6 + rnd() * 9 : 1.4 + rnd() * rnd() * 6, ry = rx * (.38 + rnd() * .45); const x = rnd() * N, y = rnd() * N; pit(x, y, rx, ry); if (x < 16) pit(x + N, y, rx, ry); if (x > N - 16) pit(x - N, y, rx, ry); if (y < 16) pit(x, y + N, rx, ry); if (y > N - 16) pit(x, y - N, rx, ry); }
    return c;
  }
  function blackStoneCanvas() {
    const N = 512, c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'), img = g.createImageData(N, N), d = img.data, rnd = rngOf(23);
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const u = x / N, v = y / N, n = fbm(u * 5, v * 5, 4), m = fbm(u * 40, v * 40, 3), vein = Math.pow(1 - Math.abs(Math.sin((u * 3 + v * 1.6 + fbm(u * 3, v * 3, 3) * 2.2) * Math.PI)), 26);
      const k = 8 + n * 7 + m * 3 + vein * 7, i = (y * N + x) * 4; d[i] = k; d[i + 1] = k; d[i + 2] = k + 1; d[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    for (let i = 0; i < 90; i++) { g.fillStyle = `rgba(190,190,190,${.05 + rnd() * .12})`; g.beginPath(); g.arc(rnd() * N, rnd() * N, .5 + rnd() * 1.1, 0, 7); g.fill(); }   // faint mineral flecks
    return c;
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

    // ---- the board: honed travertine squares (matte, pitted) and polished black-stone squares in a chunky travertine slab.
    // Only the polished black squares are see-through, so the upside-down twins of the pieces read as reflections in them.
    const mk = (canvas, rx, ry) => { const t = new THREE.CanvasTexture(canvas); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; t.repeat.set(rx, ry); return t; };
    const travTex = mk(travertineCanvas(), .5, .5), stoneTex = mk(blackStoneCanvas(), .5, .5);
    const vary = (tex, i) => { const t = tex.clone(); t.needsUpdate = true; t.center.set(.5, .5); t.rotation = (i % 4) * Math.PI / 2; t.offset.set((i % 3) * .3, Math.floor(i / 3) * .5 + i * .07); return t; };
    const lights = Array.from({ length: 6 }, (_, i) => { const t = vary(travTex, i); return new THREE.MeshStandardMaterial({ map: t, bumpMap: t, color: 0xcdc1a9, bumpScale: 3.6, roughness: .6, metalness: 0, envMapIntensity: .7 }); });
    const darks = Array.from({ length: 6 }, (_, i) => new THREE.MeshPhysicalMaterial({ map: vary(stoneTex, i), roughness: .05, clearcoat: 1, clearcoatRoughness: .02, transparent: true, opacity: .8, envMapIntensity: 1.6 }));
    const sqGeo = new THREE.BoxGeometry(.995, .06, .995);
    for (let f = 0; f < 8; f++) for (let r = 0; r < 8; r++) {
      const light = (f + r) % 2, set = light ? lights : darks, m = new THREE.Mesh(sqGeo, set[(f * 7 + r * 3) % set.length]);
      m.position.set(sqx(f), TOP - .03, sqz(r)); m.receiveShadow = true; m.renderOrder = light ? 0 : 2; scene.add(m);
    }
    const slabT = mk(travertineCanvas(), 3, .5); slabT.rotation = 0;
    const slabM = new THREE.MeshStandardMaterial({ map: slabT, bumpMap: slabT, color: 0xc4b89e, bumpScale: 3.2, roughness: .66, envMapIntensity: .7 });
    const W = 8, B = .7, H = .32;
    // dark skirt under the slab: hides the reflection twins from the sides so they only show through the black stone
    { const wallM = new THREE.MeshBasicMaterial({ color: 0x070809, side: THREE.DoubleSide }), hh = 3.4, yy = TOP - hh / 2 - .05, o = W / 2 + B - .02;
      [[0, -o, W + B * 2, .02], [0, o, W + B * 2, .02], [-o, 0, .02, W + B * 2], [o, 0, .02, W + B * 2]].forEach(([x, z, w, d]) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, hh, d), wallM); m.position.set(x, yy, z); scene.add(m); }); }
    [[0, -(W / 2 + B / 2), W + B * 2, B], [0, W / 2 + B / 2, W + B * 2, B], [-(W / 2 + B / 2), 0, B, W], [W / 2 + B / 2, 0, B, W]].forEach(([x, z, w, d]) => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, H, d), slabM); m.position.set(x, TOP + .01 - H / 2 + .03, z); m.castShadow = m.receiveShadow = true; scene.add(m);
    });
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
    camState.dist = 5.6 / (t * camera.aspect * usable);
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
