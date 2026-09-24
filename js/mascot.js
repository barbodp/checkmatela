/* "Sir Checkmate" — Checkmatela's mascot: a small, glossy, inflated 3D gentleman who floats up the screen like a
   balloon. He is NOT tied to scrolling and not confined to the hero: he rises slowly from the bottom of the viewport to
   the top, fades away, pauses, then floats up again from a different spot — wherever you are on the homepage.

   Built from primitives with three.js (vendored in js/vendor, loaded after the page has settled). The canvas is only as
   big as he is and is moved with a CSS transform, so rendering stays cheap. Click-through, sits under the header,
   skipped for reduced-motion visitors.

   Tweak: size (SIZE below + .mascot-canvas in CSS), pace / pauses / sway (RISE below), look (buildMascot()). */
(() => {
  "use strict";
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const SIZE = () => (window.innerWidth < 700 ? [150, 180] : [210, 250]);   // canvas px (w, h)
  let THREE = null, renderer, scene, camera, mascot, parts, canvas;
  // one rise = bottom → top of the viewport. Times in seconds.
  const RISE = { secs: [26, 34], pause: [1.5, 4], swayPx: [50, 130], swaySecs: [7, 11] };
  const rnd = ([a, b]) => a + Math.random() * (b - a);
  let lastX = null, lastY = null, faceY = 0, bank = 0, lean = 0, cyc = null, lastLane = -1;

  /* ------------------------------------------------------------------ the character */
  function buildMascot() {
    const T = THREE;
    const P = o => new T.MeshPhysicalMaterial(o);
    const skin = P({ color: 0xf4e4cb, roughness: .3, clearcoat: 1, clearcoatRoughness: .1 });
    const suit = P({ color: 0x0c0c0f, roughness: .26, clearcoat: 1, clearcoatRoughness: .08 });
    const shirt = P({ color: 0xfbf8f1, roughness: .38, clearcoat: .5, clearcoatRoughness: .2 });
    const tie = P({ color: 0x8a1f3a, roughness: .28, clearcoat: .9, clearcoatRoughness: .1 });
    const green = P({ color: 0x1e4d3b, roughness: .4, clearcoat: .4 });
    const brass = new T.MeshStandardMaterial({ color: 0xdcae55, metalness: 1, roughness: .2 });
    const ink = new T.MeshBasicMaterial({ color: 0x141414 });

    const g = new T.Group();
    const add = (parent, geo, mat, pos = [0, 0, 0], scl = [1, 1, 1], rot = [0, 0, 0]) => {
      const m = new T.Mesh(geo, mat);
      m.position.set(...pos); m.scale.set(...scl); m.rotation.set(...rot);
      parent.add(m); return m;
    };
    const sph = new T.SphereGeometry(1, 48, 32);

    /* body — an inflated, slightly pear-shaped torso */
    const body = new T.Group(); g.add(body);
    add(body, sph, suit, [0, 0.9, 0], [1.05, 1.22, .9]);
    add(body, sph, shirt, [0, 1.42, .62], [.44, .78, .3]);                 // shirt front
    add(body, sph, suit, [-.3, 1.52, .78], [.2, .62, .12], [0, 0, -.35]);  // lapels
    add(body, sph, suit, [.3, 1.52, .78], [.2, .62, .12], [0, 0, .35]);
    [.9, .55].forEach(y => add(body, sph, brass, [0, y, .84 + (y < .8 ? .03 : 0)], [.07, .07, .05]));
    add(body, new T.BoxGeometry(.24, .16, .04), shirt, [.55, 1.42, .82], [1, 1, 1], [0, 0, .25]);   // pocket square
    add(body, new T.BoxGeometry(.16, .08, .045), green, [.55, 1.4, .83], [1, 1, 1], [0, 0, .25]);
    // bow tie
    const bt = new T.Group(); bt.position.set(0, 1.96, .74); body.add(bt);
    add(bt, sph, tie, [0, 0, .02], [.11, .11, .1]);
    [-1, 1].forEach(s => add(bt, new T.ConeGeometry(.2, .36, 24), tie, [s * .24, 0, 0], [1, 1, .55], [0, 0, -s * Math.PI / 2]));

    /* head */
    const head = new T.Group(); head.position.set(0, 3.3, .05); head.scale.setScalar(1.22); g.add(head);
    const R = [1.02, 1.12, .98];
    add(head, sph, skin, [0, 0, 0], R);
    const surf = (x, y, lift = 0) => [x, y, R[2] * Math.sqrt(Math.max(0, 1 - (x / R[0]) ** 2 - (y / R[1]) ** 2)) + lift];
    const tube = (pts, r, mat = ink) => {
      const c = new T.CatmullRomCurve3(pts.map(p => new T.Vector3(...p)));
      const m = new T.Mesh(new T.TubeGeometry(c, 40, r, 8, false), mat); head.add(m); return m;
    };
    // eyes
    [-1, 1].forEach(s => add(head, sph, ink, surf(s * .36, .16, .0), [.075, .12, .05]));
    // brows
    [-1, 1].forEach(s => tube([surf(s * .16, .6, .012), surf(s * .36, .67, .014), surf(s * .58, .56, .012)], .02));
    // big smile + cheek creases
    const smile = []; for (let i = 0; i <= 10; i++) { const x = -.56 + i * .112; smile.push(surf(x, -.34 - .3 * Math.sin(Math.PI * i / 10), .014)); }
    tube(smile, .026);
    [-1, 1].forEach(s => tube([surf(s * .6, -.24, .012), surf(s * .66, -.3, .012), surf(s * .7, -.4, .012)], .016));
    // nose
    add(head, sph, skin, surf(0, -.08, .05), [.1, .09, .1]);
    // ears
    [-1, 1].forEach(s => add(head, sph, skin, [s * 1.0, -.02, -.02], [.17, .28, .2]));
    // monocle (brass ring + chain)
    add(head, new T.TorusGeometry(.26, .03, 12, 48), brass, surf(.36, .16, .06));
    tube([surf(.55, .0, .07), [.85, -.55, .45], [.75, -1.2, .6], [.5, -1.55, .68]], .012, brass);
    // little brass king's crown
    const crown = new T.Group(); crown.position.set(0, R[1] * .96, 0); head.add(crown);
    add(crown, new T.CylinderGeometry(.34, .42, .16, 32), brass, [0, .02, 0]);
    add(crown, new T.CylinderGeometry(.3, .34, .06, 32), brass, [0, .12, 0]);
    add(crown, new T.BoxGeometry(.08, .34, .08), brass, [0, .38, 0]);
    add(crown, new T.BoxGeometry(.26, .08, .08), brass, [0, .42, 0]);
    add(crown, sph, brass, [0, .62, 0], [.06, .06, .06]);

    /* arms */
    const arms = [-1, 1].map(s => {
      const a = new T.Group(); a.position.set(s * 1.02, 1.62, 0); g.add(a);
      add(a, new T.CapsuleGeometry(.3, .7, 12, 24), suit, [0, -.55, 0]);
      add(a, new T.CylinderGeometry(.31, .31, .14, 24), shirt, [0, -1.12, 0]);
      add(a, new T.CylinderGeometry(.05, .05, .1, 12), brass, [s * .12, -1.12, .29], [1, 1, 1], [Math.PI / 2, 0, 0]);
      add(a, sph, skin, [0, -1.42, 0], [.3, .3, .3]);
      return a;
    });
    /* legs */
    const legs = [-1, 1].map(s => {
      const l = new T.Group(); l.position.set(s * .44, -.05, 0); g.add(l);
      add(l, new T.CapsuleGeometry(.34, .8, 12, 24), suit, [0, -.7, 0]);
      add(l, sph, suit, [0, -1.5, .22], [.44, .3, .68]);
      return l;
    });
    return { g, arms, legs, head, bow: bt };
  }

  function makeEnv() {
    const T = THREE, s = new T.Scene();
    s.add(new T.Mesh(new T.BoxGeometry(30, 30, 30), new T.MeshBasicMaterial({ color: 0xb9bec2, side: T.BackSide })));
    const panel = (w, h, pos, rot, c) => {
      const m = new T.Mesh(new T.PlaneGeometry(w, h), new T.MeshBasicMaterial({ color: new T.Color(c, c, c), side: T.DoubleSide }));
      m.position.set(...pos); m.rotation.set(...rot); s.add(m);
    };
    panel(14, 14, [0, 12, 0], [Math.PI / 2, 0, 0], 8);        // big softbox above
    panel(6, 10, [-11, 2, 6], [0, Math.PI / 2.4, 0], 5);       // key light, left
    panel(4, 8, [11, 1, 4], [0, -Math.PI / 2.4, 0], 2.5);      // fill, right
    panel(10, 3, [0, -6, 8], [-.5, 0, 0], 1.2);                // bounce from below
    return s;
  }

  async function boot() {
    THREE = await import('./vendor/three-0.159.module.min.js');
    canvas = document.createElement('canvas');
    canvas.className = 'mascot-canvas'; canvas.setAttribute('aria-hidden', 'true');
    document.body.appendChild(canvas);
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.setClearColor(0x000000, 0);
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(30, 1, .1, 100);
    camera.position.set(0, 0, 16);
    const pm = new THREE.PMREMGenerator(renderer);
    scene.environment = pm.fromScene(makeEnv(), .03).texture;
    const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(-4, 6, 8); scene.add(key);
    const rim = new THREE.DirectionalLight(0xffe7c2, .8); rim.position.set(6, 2, -4); scene.add(rim);
    parts = buildMascot();
    parts.g.position.y = -1.4;                       // centre the figure in the frame
    mascot = new THREE.Group(); mascot.add(parts.g); scene.add(mascot);
    resize(); window.addEventListener('resize', resize);
    window.__mascotFrame = frame;                    // test hook
    requestAnimationFrame(frame);
  }

  function resize() {
    const [w, h] = SIZE();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(w, h, false);
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }

  /* One rise: pick a lane (never the same third of the screen twice in a row), a pace, and a sway. */
  function newCycle(t, delay = 0) {
    let lane; do { lane = Math.floor(Math.random() * 3); } while (lane === lastLane); lastLane = lane;
    const dur = rnd(RISE.secs), t0 = t + delay;
    cyc = { t0, dur, end: t0 + dur, next: t0 + dur + rnd(RISE.pause), lane: (lane + .2 + Math.random() * .6) / 3, amp: rnd(RISE.swayPx), per: rnd(RISE.swaySecs), ph: Math.random() * 6.28 };
  }
  /* position (px) + fade for time t, or null while he is resting between rises */
  function route(t) {
    const [w, h] = SIZE(), vw = window.innerWidth, vh = window.innerHeight;
    if (!cyc) newCycle(t, 1);
    if (t > cyc.next) newCycle(t);
    if (t < cyc.t0 || t > cyc.end) return null;
    const p = (t - cyc.t0) / cyc.dur;
    const x = Math.min(vw - w, Math.max(0, cyc.lane * vw - w / 2 + cyc.amp * Math.sin(((t - cyc.t0) / cyc.per) * 6.283 + cyc.ph)));
    const y = vh + 20 - p * (vh + h + 40);                       // enters just below the screen, leaves above it
    // dissolve as he nears the top of the screen (based on where he actually is, so it is always visible)
    const fade = Math.min(1, p / .05, Math.max(0, (y + h * .55) / (vh * .3)));
    return [x, y + 8 * Math.sin(t * 1.25), Math.max(0, fade)];
  }

  let last = 0, skew = 0;
  window.__mascotSeek = sec => { skew += sec; };      // test hook: fast-forward the clock
  function frame(now) {
    requestAnimationFrame(frame);
    if (document.hidden) return;
    const dt = Math.min(.05, (now - last) / 1000 || .016); last = now;
    const t = now / 1000 + skew;
    const r = route(t);
    if (!r) { canvas.style.visibility = 'hidden'; lastX = lastY = null; return; }
    const [x, y, fade] = r;
    const vx = lastX === null ? 0 : (x - lastX) / dt;
    lastX = x; lastY = y;
    // gently turn toward the sideways drift, bank into it, and lean back a little as he climbs
    const k = Math.min(1, dt * 2);
    faceY += (Math.max(-1, Math.min(1, vx / 45)) * .7 - faceY) * k;
    bank += (Math.max(-1, Math.min(1, -vx / 70)) * .2 - bank) * k;
    canvas.style.transform = `translate3d(${x.toFixed(1)}px, ${y.toFixed(1)}px, 0) scale(${(.9 + .1 * fade).toFixed(3)})`;
    canvas.style.opacity = fade.toFixed(3);
    canvas.style.visibility = 'visible';
    mascot.rotation.set(.16, faceY + Math.sin(t * .9) * .14, bank + Math.sin(t * 1.3) * .06);
    mascot.scale.setScalar(.94 * (1 + .03 * Math.sin(t * 1.7)));
    parts.arms.forEach((a, i) => { const s2 = i ? 1 : -1; a.rotation.z = s2 * (1.1 + .25 * Math.sin(t * 2.2 + i)); a.rotation.x = .14 * Math.sin(t * 2 + i * 2); });
    parts.legs.forEach((l, i) => { l.rotation.x = .3 * Math.sin(t * 2.1 + i * Math.PI); l.rotation.z = (i ? 1 : -1) * .1; });
    parts.head.rotation.z = .07 * Math.sin(t * 1.4);
    parts.bow.rotation.z = .05 * Math.sin(t * 3);
    renderer.render(scene, camera);
  }

  // start once the page has settled so the hero paints first
  const go = () => setTimeout(boot, 800);
  if (document.readyState === 'complete') go(); else window.addEventListener('load', go, { once: true });
})();
