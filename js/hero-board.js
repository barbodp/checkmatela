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
  // [type, file 0-7 (a-h), rank 0-7 (1-8)] — white pieces are clickable, black ones are scenery. Landing squares are kept empty.
  const WHITE = [['rook', 0, 0], ['bishop', 2, 0], ['queen', 3, 0], ['king', 4, 0], ['bishop', 5, 0], ['knight', 6, 0], ['rook', 7, 0],
                 ['pawn', 1, 1], ['pawn', 3, 1], ['pawn', 5, 1], ['pawn', 6, 1], ['pawn', 7, 1]];
  const BLACK = [['rook', 0, 7], ['bishop', 2, 7], ['queen', 3, 7], ['king', 4, 7], ['bishop', 5, 7], ['knight', 6, 7], ['rook', 7, 7],
                 ['pawn', 0, 6], ['pawn', 2, 6], ['pawn', 4, 6], ['pawn', 6, 6], ['pawn', 7, 6], ['pawn', 3, 4], ['knight', 2, 5]];
  // how each type moves when clicked: [file delta, rank delta] and how high it hops
  const MOVES = { pawn: [0, 2, .55], rook: [0, 3, 1.5], bishop: [2, 2, 1.1], queen: [3, 3, 1.1], king: [0, 1, .7], knight: [-1, 2, 1.3] };
  const MOVE_BISHOP_LEFT = -2;                                  // the f1 bishop goes up-left, the c1 bishop up-right

  let THREE = null, renderer, scene, camera, ground, ring, envTex;
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
    const T3 = THREE;
    const ivory = new T3.MeshPhysicalMaterial({ color: 0xf3ead6, roughness: .34, clearcoat: .7, clearcoatRoughness: .18 });
    const ebony = new T3.MeshPhysicalMaterial({ color: 0x18191b, roughness: .26, clearcoat: 1, clearcoatRoughness: .1 });
    const brass = new T3.MeshStandardMaterial({ color: 0xd8aa52, metalness: 1, roughness: .22 });
    return { ivory, ebony, brass };
  }
  const geoCache = {};
  function G(key, make) { return geoCache[key] || (geoCache[key] = make()); }
  const lathe = (pts, seg = 40) => new THREE.LatheGeometry(new THREE.SplineCurve(pts.map(p => new THREE.Vector2(p[0], p[1]))).getPoints(40), seg);
  const cyl = (rt, rb, h, seg = 40) => new THREE.CylinderGeometry(rt, rb, h, seg);

  function buildPiece(type, body, trim) {
    const g = new THREE.Group(), add = (geo, mat, x = 0, y = 0, z = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m; };
    // shared base
    add(G('b1', () => cyl(.42, .44, .07)), body, 0, .035);
    add(G('b2', () => cyl(.35, .38, .08)), body, 0, .11);
    let h = 1;
    if (type === 'pawn') {
      add(G('pawnB', () => lathe([[.3, .14], [.22, .28], [.14, .5], [.115, .64]])), body);
      add(G('pawnC', () => cyl(.2, .2, .05)), trim, 0, .68);
      add(G('pawnH', () => new THREE.SphereGeometry(.19, 32, 24)), body, 0, .84); h = 1.05;
    } else if (type === 'rook') {
      add(G('rookB', () => lathe([[.32, .14], [.26, .3], [.22, .7], [.24, .84]])), body);
      add(G('rookT', () => cyl(.31, .27, .17)), body, 0, .93);
      add(G('rookC', () => cyl(.24, .24, .05)), trim, 0, .82);
      for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2, m = add(G('mer', () => new THREE.BoxGeometry(.14, .13, .13)), body, Math.sin(a) * .25, 1.06, Math.cos(a) * .25); m.rotation.y = a; }
      h = 1.2;
    } else if (type === 'bishop') {
      add(G('bisB', () => lathe([[.31, .14], [.2, .35], [.13, .7], [.12, .8]])), body);
      add(G('bisC', () => cyl(.2, .2, .05)), trim, 0, .82);
      add(G('bisH', () => lathe([[0, .84], [.15, .89], [.22, 1.05], [.2, 1.22], [.1, 1.38], [0, 1.44]])), body);
      add(G('bisT', () => new THREE.SphereGeometry(.06, 20, 16)), trim, 0, 1.47);
      const slit = add(G('slit', () => new THREE.BoxGeometry(.4, .03, .04)), new THREE.MeshStandardMaterial({ color: 0x2b2b2b, roughness: .6 }), 0, 1.16, .0); slit.rotation.z = -.75; slit.castShadow = false;
      h = 1.5;
    } else if (type === 'queen') {
      add(G('queB', () => lathe([[.33, .14], [.22, .4], [.15, .8], [.14, .95]])), body);
      add(G('queC', () => cyl(.26, .26, .05)), trim, 0, 1.0);
      add(G('queH', () => lathe([[.16, 1.04], [.22, 1.2], [.26, 1.36], [.23, 1.46]])), body);
      for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; add(G('qb', () => new THREE.SphereGeometry(.045, 12, 10)), trim, Math.sin(a) * .235, 1.48, Math.cos(a) * .235); }
      add(G('queT', () => new THREE.SphereGeometry(.085, 20, 16)), trim, 0, 1.56); h = 1.7;
    } else if (type === 'king') {
      add(G('kinB', () => lathe([[.33, .14], [.22, .4], [.15, .8], [.14, .95]])), body);
      add(G('kinC', () => cyl(.26, .26, .05)), trim, 0, 1.0);
      add(G('kinH', () => lathe([[.16, 1.04], [.23, 1.22], [.27, 1.4], [.24, 1.52]])), body);
      add(G('kinT', () => cyl(.2, .22, .05)), trim, 0, 1.55);
      add(G('kv', () => new THREE.BoxGeometry(.075, .3, .075)), trim, 0, 1.76); add(G('kh', () => new THREE.BoxGeometry(.24, .075, .075)), trim, 0, 1.79); h = 1.95;
    } else if (type === 'knight') {
      add(G('knB', () => lathe([[.3, .14], [.22, .36], [.2, .56]])), body);
      add(G('knC', () => cyl(.24, .24, .05)), trim, 0, .58);
      const geo = G('knH', () => {
        const pts = [[-.2, .6], [-.25, .78], [-.22, 1.0], [-.12, 1.16], [-.02, 1.24], [.05, 1.34], [.1, 1.24], [.22, 1.14], [.42, .96], [.45, .86], [.36, .8], [.25, .86], [.14, .82], [.22, .72], [.3, .62], [-.2, .6]];
        const shape = new THREE.Shape(new THREE.SplineCurve(pts.map(p => new THREE.Vector2(p[0], p[1]))).getPoints(90));
        const e = new THREE.ExtrudeGeometry(shape, { depth: .22, bevelEnabled: true, bevelSize: .05, bevelThickness: .05, bevelSegments: 4, curveSegments: 12 });
        e.translate(0, 0, -.11); return e;
      });
      const m = add(geo, body); m.rotation.y = Math.PI / 2; h = 1.35;
      [-1, 1].forEach(sd => { const e = add(G('eye', () => new THREE.SphereGeometry(.03, 12, 10)), new THREE.MeshBasicMaterial({ color: 0x111111 }), sd * .165, 1.12, -.1); e.castShadow = false; });
    }
    g.userData.h = h;
    return g;
  }

  function addPiece(type, file, rank, white, M) {
    const bodyMat = M[white ? 'ivory' : 'ebony'].clone();
    const trim = white ? M.brass : M.brass;
    const g = buildPiece(type, bodyMat, white ? trim : new THREE.MeshPhysicalMaterial({ color: 0x2a2c2e, roughness: .3, clearcoat: 1 }));
    g.position.set(sqx(file), TOP, sqz(rank));
    if (!white) g.rotation.y = Math.PI;
    if (type === 'knight') g.rotation.y += (white ? 1 : -1) * (file > 3 ? -.75 : .75);
    scene.add(g);
    const p = { type, white, group: g, file, rank, mat: bodyMat, home: g.position.clone(), homeRot: g.rotation.y, lift: 0, glow: 0, h: g.userData.h };
    g.traverse(o => { if (o.isMesh) o.userData.piece = p; });
    pieces.push(p); if (white) interactive.push(p);
    return p;
  }

  /* ---------------------------------------------------------------- scene */
  function makeEnv() {
    const s = new THREE.Scene();
    s.add(new THREE.Mesh(new THREE.BoxGeometry(40, 40, 40), new THREE.MeshBasicMaterial({ color: 0xc9cdd0, side: THREE.BackSide })));
    const panel = (w, h, pos, rot, c) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(c, c, c), side: THREE.DoubleSide })); m.position.set(...pos); m.rotation.set(...rot); s.add(m); };
    panel(16, 16, [0, 14, 0], [Math.PI / 2, 0, 0], 7); panel(6, 12, [-12, 4, 6], [0, Math.PI / 2.3, 0], 4); panel(5, 9, [12, 3, 4], [0, -Math.PI / 2.3, 0], 2.2);
    return s;
  }

  async function boot() {
    THREE = await import('./vendor/three-0.159.module.min.js');
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.02;
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; renderer.setClearColor(0, 0);
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(30, 1, .1, 100);
    const pm = new THREE.PMREMGenerator(renderer); envTex = pm.fromScene(makeEnv(), .03).texture; scene.environment = envTex;
    const sun = new THREE.DirectionalLight(0xffffff, 2.1); sun.position.set(-5, 10, 6); sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 }); sun.shadow.bias = -.0004; sun.shadow.radius = 4;
    scene.add(sun); const fill = new THREE.DirectionalLight(0xffe9c8, .5); fill.position.set(6, 4, -3); scene.add(fill);

    // board: dark-pine frame, brass inlay line, 8×8 squares
    const frame = new THREE.Mesh(new THREE.BoxGeometry(8.7, .3, 8.7), new THREE.MeshPhysicalMaterial({ color: 0x0f2e22, roughness: .4, clearcoat: .6 })); frame.position.y = -.05; frame.castShadow = frame.receiveShadow = true; scene.add(frame);
    const brass = new THREE.MeshStandardMaterial({ color: 0xd8aa52, metalness: 1, roughness: .25 });
    [[0, -4.03, 8.1, .05], [0, 4.03, 8.1, .05], [-4.03, 0, .05, 8.1], [4.03, 0, .05, 8.1]].forEach(([x, z, w, d]) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, .02, d), brass); m.position.set(x, .105, z); scene.add(m); });
    const light = new THREE.MeshPhysicalMaterial({ color: 0xf1e9d8, roughness: .5, clearcoat: .3 }), dark = new THREE.MeshPhysicalMaterial({ color: 0x141517, roughness: .55, clearcoat: .2, envMapIntensity: .55 });
    const sqGeo = new THREE.BoxGeometry(1, .06, 1);
    for (let f = 0; f < 8; f++) for (let r = 0; r < 8; r++) { const m = new THREE.Mesh(sqGeo, (f + r) % 2 ? light : dark); m.position.set(sqx(f), TOP - .03, sqz(r)); m.receiveShadow = true; scene.add(m); }
    ground = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShadowMaterial({ opacity: .16 })); ground.rotation.x = -Math.PI / 2; ground.position.y = -.2; ground.receiveShadow = true; scene.add(ground);
    ring = new THREE.Mesh(new THREE.RingGeometry(.37, .47, 56), new THREE.MeshBasicMaterial({ color: 0xd8aa52, transparent: true, opacity: 0, side: THREE.DoubleSide })); ring.rotation.x = -Math.PI / 2; ring.position.y = TOP + .004; scene.add(ring);

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
    const wide = w > 900, usable = wide ? .5 : .92;
    const t = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    const dH = 5.0 / (t * camera.aspect * usable), dV = 5.9 / t;
    camState.dist = Math.max(dH, wide ? dV : dH);
    camera.setViewOffset(w, h, wide ? -w * .155 : 0, wide ? h * .07 : -h * .1, w, h);
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
  const home = type => interactive.find(p => p.type === type && (type !== 'bishop' || p.file === 5)) || interactive.find(p => p.type === type);

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
    let [df, dr, hop] = MOVES[p.type]; if (p.type === 'bishop' && p.file === 5) df = MOVE_BISHOP_LEFT;
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
    const el = THREE.MathUtils.degToRad(40), d = camState.dist;
    camState.x += ((pointer.in ? pointer.x : 0) - camState.x) * Math.min(1, dt * 2.2); camState.y += ((pointer.in ? pointer.y : 0) - camState.y) * Math.min(1, dt * 2.2);
    const yaw = camState.x * .09 + Math.sin(T * .18) * .035, elv = el + camState.y * .03;
    const target = new THREE.Vector3(0, .5, .35), pos = new THREE.Vector3(Math.sin(yaw) * Math.cos(elv) * d, Math.sin(elv) * d + .5, Math.cos(yaw) * Math.cos(elv) * d + .35);
    if (dive) {
      const k = easeIO(dive.k || 0);
      camera.position.lerpVectors(pos, dive.to, k); target.lerp(dive.look, k); camera.fov = lerp(30, dive.fov, k); camera.updateProjectionMatrix();
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
    if (hovered && !busy) { ring.position.set(hovered.home.x, TOP + .004, hovered.home.z); ring.material.opacity += (.9 - ring.material.opacity) * Math.min(1, dt * 10); }
    else ring.material.opacity += (0 - ring.material.opacity) * Math.min(1, dt * 10);
    // idle: every few seconds one piece nudges to say "I'm clickable"
    if (!busy && !hovered && T > idleAt) { const p = interactive[Math.floor(Math.random() * interactive.length)]; p.nudge = T; idleAt = T + 3.5 + Math.random() * 3; }
    placeCamera(dt);
    if (tip.classList.contains('is-on')) {
      const p = hovered || interactive.find(q => q.group.position.y > TOP + .3);
      if (p) { const v = p.group.position.clone(); v.y += p.h + .35; v.project(camera); const r = canvas.getBoundingClientRect(); tip.style.transform = `translate(${((v.x + 1) / 2) * r.width}px, ${((1 - v.y) / 2) * r.height}px) translate(-50%, -100%)`; }
    }
    renderer.render(scene, camera);
  }
  let last = 0;
  function loop(now) { requestAnimationFrame(loop); if (document.hidden) return; const dt = Math.min(.05, (now - last) / 1000 || .016); last = now; update(dt); }

  /* ---------------------------------------------------------------- start */
  const webgl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; } })();
  window.__hb = { advance(sec) { for (let i = 0; i < Math.round(sec / .02); i++) update(.02); }, get state() { return { busy, hovered: hovered && hovered.type, pieces: pieces.length }; }, noNav: false, hover(t) { setHover(home(t)); }, click(t) { return choose(home(t)); } };
  keys.forEach(k => k.addEventListener('click', e => { if (!root.classList.contains('is-ready')) return; }));
  if (!webgl || reduce) { root.classList.add('is-fallback'); return; }
  boot().catch(() => root.classList.add('is-fallback'));
})();
